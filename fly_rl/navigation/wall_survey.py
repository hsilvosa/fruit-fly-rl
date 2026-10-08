"""Survey an observed blocking surface when no opening has been discovered."""
import numpy as np
from fly_rl.navigation.segmented_goal import SegmentedGoalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-wall-survey-exp1'
from fly_rl.navigation.room_aware import RoomAwareController

class WallSurveyController(SegmentedGoalController):
    def __init__(self, room_size=(64., 64., 20.)):
        super().__init__(room_size)
        self.survey = None
        self.no_opening_since = None
        self.survey_count = 0

    def blocking_surface(self, values):
        ranges = np.clip(values[269:2069] * 24, .05, 24)
        directions = self.directions @ self.rotation().T
        points = directions * ranges[:, None]
        z = points[:, 2] + self.position[2]
        keep = (ranges < 23.4) & (z > .5) & (z < self.room_size[2] - .5)
        points = points[keep]
        xy = points[:, :2]
        if len(xy) < 80:
            return None
        toward = (self.initial_goal - self.position)[:2]
        toward /= max(np.linalg.norm(toward), 1e-8)
        best = None
        for i, j in np.random.default_rng(42).integers(len(xy), size=(48, 2)):
            delta = xy[j] - xy[i]
            length = np.linalg.norm(delta)
            if length < 1:
                continue
            normal = np.array([delta[1], -delta[0]]) / length
            if normal @ toward < 0:
                normal = -normal
            distance = float(xy[i] @ normal)
            if normal @ toward < .5 or not .5 < distance < 4:
                continue
            inliers = np.abs(xy @ normal - distance) < .12
            if inliers.sum() < 80:
                continue
            _, vectors = np.linalg.eigh(np.cov(xy[inliers].T))
            normal = vectors[:, 0]
            if normal @ toward < 0:
                normal = -normal
            distance = float(np.median(xy[inliers] @ normal))
            tangent = np.array([-normal[1], normal[0]])
            if (not .5 < distance < 4 or normal @ toward < .5
                    or np.ptp(xy[inliers] @ tangent) < 8
                    or np.ptp(points[inliers, 2]) < min(.65 * self.room_size[2], 3 * distance)):
                continue
            score = float(inliers.sum()) * float(normal @ toward) ** 2
            if best is None or score > best[0]:
                best = (score, np.r_[normal, 0.], distance)
        if best is None:
            return None
        _, normal, distance = best
        return dict(normal=normal, center=self.position + normal * distance)

    def survey_destination(self, surface):
        if self.survey is None:
            normal = surface['normal']
            tangent = np.array([-normal[1], normal[0], 0.])
            direction = 1 if (self.initial_goal - self.position) @ tangent >= 0 else -1
            center = surface['center'].copy()
            center[2] = self.room_size[2] / 2
            target = center - normal * 2 + tangent * direction * 4
            self.survey = dict(center=center, normal=normal, tangent=tangent,
                               direction=direction, target=target, last_progress=self.tick,
                               best_distance=np.inf, reversals=0)
            self.survey_count += 1
            self.reference = None
        survey = self.survey
        distance = float(np.linalg.norm(survey['target'] - self.position))
        if distance < survey['best_distance'] - .3:
            survey['best_distance'] = distance
            survey['last_progress'] = self.tick
        if distance < .8:
            survey['target'] += survey['tangent'] * survey['direction'] * 4
            survey['best_distance'] = np.inf
            survey['last_progress'] = self.tick
            self.reference = None
        elif self.tick - survey['last_progress'] >= 160:
            survey['direction'] *= -1
            survey['target'] = (self.position - survey['normal'] *
                ((self.position - survey['center']) @ survey['normal'] + 2)
                + survey['tangent'] * survey['direction'] * 4)
            survey['target'][2] = self.room_size[2] / 2
            survey['reversals'] += 1
            survey['best_distance'] = np.inf
            survey['last_progress'] = self.tick
            self.reference = None
        return survey['target'].copy()

    def plan(self, goal):
        super().plan(goal)
        if self.portal is not None or self.direct_goal_visible(self.current_values):
            self.survey = None
            self.no_opening_since = None
        elif self.room_size[2] == 20:
            surface = self.blocking_surface(self.current_values)
            if self.survey is not None and (self.position - self.survey['center']) @ self.survey['normal'] > .9:
                self.survey = None
                self.no_opening_since = None
            if surface is not None or self.survey is not None:
                if self.no_opening_since is None:
                    self.no_opening_since = self.tick
                if self.tick - self.no_opening_since >= 80:
                    destination = self.survey_destination(surface)
                    RoomAwareController.plan(self, destination)
            else:
                self.no_opening_since = None
        self.debug.update(wall_survey_active=self.survey is not None,
            wall_surveys=self.survey_count,
            wall_survey_target=self.survey['target'].tolist() if self.survey is not None else None,
            wall_survey_reversals=self.survey['reversals'] if self.survey is not None else 0)
