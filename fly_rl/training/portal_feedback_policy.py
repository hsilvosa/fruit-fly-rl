"""Learned neural waypoint perception with explicit coordinated flight feedback.

Only recurrent neural histories enter this policy. Portal and velocity labels
are training supervision, never runtime observations. No route is accessed.
"""
import numpy as np
import torch
from torch import nn
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from fly_rl.training.panorama_policy import CircularConv
from fly_rl.simulation.sensors import SENSORS, PANORAMA_SHAPE, panorama_directions


def feedback_actions(delta, velocity):
    """Differentiable PD control for a perceived body-frame waypoint."""
    distance = torch.linalg.vector_norm(delta, dim=1).clamp_min(1e-6)
    error = torch.atan2(delta[:, 1], delta[:, 0])
    speed = torch.minimum(distance * 1.5, torch.full_like(distance, 1.2))
    speed = speed * torch.cos(error).clamp_min(0).pow(4)
    desired = delta / distance[:, None] * speed[:, None]
    horizontal = torch.linalg.vector_norm(desired[:, :2], dim=1)
    thrust = (3 * (horizontal - velocity[:, 0]) + .6 * horizontal).clamp(-1.2, 3)
    forward = torch.where(thrust >= 0, thrust / 3, thrust / 1.2)
    vertical = ((3 * (desired[:, 2] - velocity[:, 2]) + .8 * desired[:, 2]) / 2.5).clamp(-1, 1)
    return torch.stack([forward, torch.zeros_like(forward), vertical, (error * 2 / 1.8).clamp(-1, 1)], dim=1)


class PortalNeuralFeatures(BaseFeaturesExtractor):
    def __init__(self, observation_space):
        if len(observation_space.shape) != 2 or observation_space.shape[1] != 3869:
            raise ValueError('Portal feedback requires v6 neural histories')
        super().__init__(observation_space, features_dim=6)
        self.register_buffer('directions', torch.tensor(panorama_directions(), dtype=torch.float32))
        # Current and most recent stored activity, with angular coordinates and
        # a goal-bearing prior. These are transformations of neural values.
        self.image = nn.Sequential(CircularConv(7, 16), nn.Tanh(), CircularConv(16, 24), nn.Tanh(),
                                   CircularConv(24, 24), nn.Tanh())
        self.score = nn.Conv2d(24, 1, 1)
        self.proprio = nn.Sequential(nn.Linear(SENSORS * 2, 64), nn.Tanh())
        self.range_head = nn.Sequential(nn.Linear(88, 64), nn.Tanh(), nn.Linear(64, 1))
        self.offset_head = nn.Sequential(nn.Linear(88, 64), nn.Tanh(), nn.Linear(64, 3))
        self.velocity_head = nn.Linear(SENSORS * 2, 3)
        nn.init.zeros_(self.offset_head[-1].weight)
        nn.init.zeros_(self.offset_head[-1].bias)

    def perception(self, observations):
        values = observations[:, -1] * 8
        previous = observations[:, -2] * 8
        goal = values[:, 256:259]
        goal = goal / torch.linalg.vector_norm(goal, dim=1, keepdim=True).clamp_min(1e-6)
        shape = PANORAMA_SHAPE
        coords = self.directions.T.reshape(1, 3, *shape).expand(len(values), -1, -1, -1)
        goal_map = goal[:, :, None, None].expand(-1, -1, *shape)
        depth = torch.stack([values[:, SENSORS:SENSORS + 1800],
                             previous[:, SENSORS:SENSORS + 1800]], dim=1).reshape(-1, 2, *shape)
        # Dot product supplies one scalar bearing channel; no absolute pose.
        alignment = (coords * goal_map).sum(1, keepdim=True)
        image = self.image(torch.cat([depth, coords, alignment, values[:, 259:260, None, None].expand(-1, -1, *shape)], dim=1))
        logits = self.score(image).flatten(1) + 2 * (goal @ self.directions.T)
        weights = logits.softmax(1)
        direction = weights @ self.directions
        pooled = (image.flatten(2) * weights[:, None]).sum(2)
        proprio = torch.cat([values[:, :SENSORS], previous[:, :SENSORS]], dim=1)
        combined = torch.cat([pooled, self.proprio(proprio)], dim=1)
        direction = direction + .15 * torch.tanh(self.offset_head(combined))
        direction = direction / torch.linalg.vector_norm(direction, dim=1, keepdim=True).clamp_min(1e-6)
        distance = torch.nn.functional.softplus(self.range_head(combined)).clamp_max(3) * 12
        delta = direction * distance
        velocity = self.velocity_head(proprio)
        return torch.cat([delta, velocity], dim=1), logits

    def forward(self, observations):
        return self.perception(observations)[0]

    def forward_with_waypoint(self, observations):
        features = self.forward(observations)
        distance = torch.linalg.vector_norm(features[:, :3], dim=1, keepdim=True).clamp_min(1e-6)
        return features, torch.cat([features[:, :3] / distance, distance / 24], dim=1)


class PortalFeedbackPolicy(ActorCriticPolicy):
    """PPO-compatible Gaussian mean derived from learned neural perception."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('features_extractor_class', PortalNeuralFeatures)
        kwargs.update(net_arch=[], ortho_init=False, share_features_extractor=True)
        super().__init__(*args, **kwargs)

    def _get_action_dist_from_latent(self, latent_pi):
        mean = feedback_actions(latent_pi[:, :3], latent_pi[:, 3:6])
        return self.action_dist.proba_distribution(mean, self.log_std)


class EquivariantPortalNeuralFeatures(PortalNeuralFeatures):
    """Yaw-equivariant bearing: never expose a fixed body azimuth to CNN scores."""
    def __init__(self, observation_space):
        super().__init__(observation_space)
        self.image = nn.Sequential(CircularConv(5, 16), nn.Tanh(), CircularConv(16, 24), nn.Tanh(),
                                   CircularConv(24, 24), nn.Tanh())

    def perception(self, observations):
        values = observations[:, -1] * 8
        previous = observations[:, -2] * 8
        goal = values[:, 256:259]
        goal = goal / torch.linalg.vector_norm(goal, dim=1, keepdim=True).clamp_min(1e-6)
        shape = PANORAMA_SHAPE
        coords = self.directions.T.reshape(1, 3, *shape).expand(len(values), -1, -1, -1)
        depth = torch.stack([values[:, SENSORS:SENSORS + 1800],
                             previous[:, SENSORS:SENSORS + 1800]], dim=1).reshape(-1, 2, *shape)
        alignment = (coords * goal[:, :, None, None]).sum(1, keepdim=True)
        image = self.image(torch.cat([depth, alignment, coords[:, 2:3],
                                     values[:, 259:260, None, None].expand(-1, -1, *shape)], dim=1))
        logits = self.score(image).flatten(1) + 2 * (goal @ self.directions.T)
        weights = logits.softmax(1)
        direction = weights @ self.directions
        direction = direction / torch.linalg.vector_norm(direction, dim=1, keepdim=True).clamp_min(1e-6)
        pooled = (image.flatten(2) * weights[:, None]).sum(2)
        proprio = torch.cat([values[:, :SENSORS], previous[:, :SENSORS]], dim=1)
        combined = torch.cat([pooled, self.proprio(proprio)], dim=1)
        distance = torch.nn.functional.softplus(self.range_head(combined)).clamp_max(3) * 12
        return torch.cat([direction * distance, self.velocity_head(proprio)], dim=1), logits


class EquivariantPortalFeedbackPolicy(PortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = EquivariantPortalNeuralFeatures
        super().__init__(*args, **kwargs)


class WhitenedPortalNeuralFeatures(EquivariantPortalNeuralFeatures):
    """Explicitly separate the new least-squares activity feature contract."""
    def perception(self, observations):
        perceived, logits = super().perception(observations / 8)
        # This readout retains projected recurrence; these channels estimate
        # local velocity and are not an appended world-state measurement.
        velocity = observations[:, -1, 260:263] * 3
        return torch.cat([perceived[:, :3], velocity], dim=1), logits


class WhitenedPortalFeedbackPolicy(PortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = WhitenedPortalNeuralFeatures
        super().__init__(*args, **kwargs)


class LocalPeakPortalNeuralFeatures(WhitenedPortalNeuralFeatures):
    """Commit attention to one local mode in the observed goal hemisphere."""
    goal_candidate_minimum = .05
    minimum_view_clearance = 0.
    def perception(self, observations):
        values = observations[:, -1]
        previous = observations[:, -2]
        goal = values[:, 256:259]
        norm = goal.norm(dim=1, keepdim=True)
        goal = goal / norm.clamp_min(1e-6)
        shape = PANORAMA_SHAPE
        coords = self.directions.T.reshape(1, 3, *shape).expand(len(values), -1, -1, -1)
        depth = torch.stack([values[:, SENSORS:SENSORS + 1800], previous[:, SENSORS:SENSORS + 1800]], dim=1).reshape(-1, 2, *shape)
        alignment = (coords * goal[:, :, None, None]).sum(1, keepdim=True)
        image = self.image(torch.cat([depth, alignment, coords[:, 2:3], values[:, 259:260, None, None].expand(-1, -1, *shape)], dim=1))
        bearing = goal @ self.directions.T
        logits = self.score(image).flatten(1) + 2 * bearing
        candidates = (bearing >= self.goal_candidate_minimum) | (norm <= 1e-6)
        if self.minimum_view_clearance > 0:
            free = candidates & (values[:, SENSORS:SENSORS + 1800] * 24 >= self.minimum_view_clearance)
            candidates = torch.where(free.any(1, keepdim=True), free, candidates)
        maximum = logits.masked_fill(~candidates, -torch.inf).argmax(1)
        row, column = maximum // 72, maximum % 72
        rows = torch.arange(25, device=values.device)[None, :, None] - row[:, None, None]
        columns = (torch.arange(72, device=values.device)[None, None, :] - column[:, None, None] + 36) % 72 - 36
        patch = ((rows.abs() <= 1) & (columns.abs() <= 1)).flatten(1) & candidates
        weights = logits.masked_fill(~patch, -torch.inf).softmax(1)
        direction = weights @ self.directions
        direction = direction / direction.norm(dim=1, keepdim=True).clamp_min(1e-6)
        pooled = (image.flatten(2) * weights[:, None]).sum(2)
        proprio = torch.cat([values[:, :SENSORS], previous[:, :SENSORS]], dim=1)
        combined = torch.cat([pooled, self.proprio(proprio)], dim=1)
        distance = torch.nn.functional.softplus(self.range_head(combined)).clamp_max(3) * 12
        return torch.cat([direction * distance, values[:, 260:263] * 3], dim=1), logits


class LocalPeakPortalFeedbackPolicy(PortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = LocalPeakPortalNeuralFeatures
        super().__init__(*args, **kwargs)


class CenteredPortalNeuralFeatures(LocalPeakPortalNeuralFeatures):
    """Perceive a visible opening center, then aim slightly through its plane."""
    def __init__(self, observation_space):
        super().__init__(observation_space)
        self.register_buffer('room_distance_scale', torch.tensor(float(np.linalg.norm(np.array([48., 48., 16.]) - .32))))

    def forward(self, observations):
        center, _ = self.perception(observations)
        goal = observations[:, -1, 256:259]
        goal = goal / goal.norm(dim=1, keepdim=True).clamp_min(1e-6)
        distance = (observations[:, -1, 259:260] * self.room_distance_scale).clamp_min(0)
        target = center[:, :3] + .9 * goal
        # Close to the observed objective use its existing neuronal bearing and
        # distance. No hidden target coordinate or route is accessed.
        target = torch.where(distance < 2, goal * distance, target)
        return torch.cat([target, center[:, 3:]], dim=1)


class CenteredPortalFeedbackPolicy(PortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = CenteredPortalNeuralFeatures
        super().__init__(*args, **kwargs)


class GuardedPortalNeuralFeatures(CenteredPortalNeuralFeatures):
    """Permit sideways detours and expose neural estimates of stopping space."""
    goal_candidate_minimum = -0.8660254
    stopping_cone_cosine = .9396926

    def __init__(self, observation_space):
        super().__init__(observation_space)
        from fly_rl.simulation.sensors import DIRECTIONS
        self.register_buffer('short_directions', torch.tensor(DIRECTIONS, dtype=torch.float32))
        self._features_dim = 9

    def forward(self, observations):
        perceived = super().forward(observations)
        ranges = (observations[:, -1, :128] * 8).clamp(0, 8)
        motion = perceived[:, 3:6].clone(); motion[:, 2] = 0
        norm = motion.norm(dim=1, keepdim=True)
        motion = motion / norm.clamp_min(1e-6)
        motion = torch.where(norm > .1, motion, torch.tensor([1., 0., 0.], device=motion.device))
        cone = motion @ self.short_directions.T >= self.stopping_cone_cosine
        ahead = ranges.masked_fill(~cone, torch.inf).min(1).values
        up = ranges.masked_fill(self.short_directions[:, 2][None] < .9396926, torch.inf).min(1).values
        down = ranges.masked_fill(self.short_directions[:, 2][None] > -.9396926, torch.inf).min(1).values
        return torch.cat([perceived, torch.stack([ahead, up, down], 1)], 1)


def guarded_feedback_actions(features):
    delta, velocity = features[:, :3], features[:, 3:6]
    actions = feedback_actions(delta, velocity)
    speed = velocity[:, :2].norm(dim=1)
    stopping = .3 + speed.square() / 2.4 + .05 * speed
    brake = -(3 * velocity[:, 0].clamp_min(0) / 1.2).clamp_max(1)
    forward = torch.where(features[:, 6] < stopping, torch.minimum(actions[:, 0], brake), actions[:, 0])
    upward = velocity[:, 2].clamp_min(0)
    downward = (-velocity[:, 2]).clamp_min(0)
    vertical = torch.where(features[:, 7] < .3 + upward.square() / 5,
                           torch.minimum(actions[:, 2], -(3 * upward / 2.5).clamp_max(1)), actions[:, 2])
    vertical = torch.where(features[:, 8] < .3 + downward.square() / 5,
                           torch.maximum(vertical, (3 * downward / 2.5).clamp_max(1)), vertical)
    return torch.stack([forward, actions[:, 1], vertical, actions[:, 3]], dim=1)


class GuardedPortalFeedbackPolicy(PortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = GuardedPortalNeuralFeatures
        super().__init__(*args, **kwargs)

    def _get_action_dist_from_latent(self, latent_pi):
        return self.action_dist.proba_distribution(guarded_feedback_actions(latent_pi), self.log_std)


class FreeSpacePortalNeuralFeatures(GuardedPortalNeuralFeatures):
    minimum_view_clearance = 1.5
    stopping_cone_cosine = .7071068


class FreeSpacePortalFeedbackPolicy(GuardedPortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        # Bypass the guard subclass's fixed extractor selection while retaining
        # its Gaussian mean and training/evaluation distribution behavior.
        kwargs['features_extractor_class'] = FreeSpacePortalNeuralFeatures
        PortalFeedbackPolicy.__init__(self, *args, **kwargs)


class ContextPortalNeuralFeatures(FreeSpacePortalNeuralFeatures):
    """Condition local aperture scores on the complete observed panorama."""
    def __init__(self, observation_space):
        super().__init__(observation_space)
        self.context = nn.Sequential(nn.AdaptiveAvgPool2d((5, 12)), nn.Flatten(),
                                     nn.Linear(24 * 5 * 12, 64), nn.Tanh(), nn.Linear(64, 48))
        nn.init.zeros_(self.context[-1].weight)
        nn.init.zeros_(self.context[-1].bias)
        self.image.register_forward_hook(self._condition)

    def _condition(self, module, inputs, output):
        scale, bias = self.context(output).chunk(2, dim=1)
        return torch.tanh(output * (1 + .25 * torch.tanh(scale[:, :, None, None]))
                          + bias[:, :, None, None])


class ContextPortalFeedbackPolicy(GuardedPortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = ContextPortalNeuralFeatures
        PortalFeedbackPolicy.__init__(self, *args, **kwargs)


class ApproachContextPortalNeuralFeatures(ContextPortalNeuralFeatures):
    """Align at a stand-off before aiming through the perceived opening."""
    def __init__(self, observation_space):
        super().__init__(observation_space)
        self.normal_head = nn.Sequential(nn.AdaptiveAvgPool2d((5, 12)), nn.Flatten(),
                                         nn.Linear(24 * 5 * 12, 64), nn.Tanh(), nn.Linear(64, 2))

    def normal(self, observations):
        values, previous = observations[:, -1], observations[:, -2]
        goal = values[:, 256:259]
        goal = goal / goal.norm(dim=1, keepdim=True).clamp_min(1e-6)
        shape = PANORAMA_SHAPE
        coords = self.directions.T.reshape(1, 3, *shape).expand(len(values), -1, -1, -1)
        depth = torch.stack([values[:, SENSORS:SENSORS + 1800], previous[:, SENSORS:SENSORS + 1800]], dim=1).reshape(-1, 2, *shape)
        alignment = (coords * goal[:, :, None, None]).sum(1, keepdim=True)
        image = self.image(torch.cat([depth, alignment, coords[:, 2:3],
                                    values[:, 259:260, None, None].expand(-1, -1, *shape)], dim=1))
        normal_xy = self.normal_head(image)
        normal_xy = normal_xy / normal_xy.norm(dim=1, keepdim=True).clamp_min(1e-6)
        return torch.cat([normal_xy, torch.zeros_like(normal_xy[:, :1])], dim=1)

    def forward(self, observations):
        center, _ = self.perception(observations)
        normal = self.normal(observations)
        longitudinal = (center[:, :3] * normal).sum(1, keepdim=True)
        offset = center[:, :3] - normal * longitudinal
        aligned = (offset.norm(dim=1, keepdim=True) < .55) & (longitudinal < 2.)
        target = torch.where(aligned, center[:, :3] + 1.2 * normal, center[:, :3] - 1.3 * normal)
        goal = observations[:, -1, 256:259]
        goal = goal / goal.norm(dim=1, keepdim=True).clamp_min(1e-6)
        distance = (observations[:, -1, 259:260] * self.room_distance_scale).clamp_min(0)
        target = torch.where(distance < 2, goal * distance, target)
        perceived = torch.cat([target, center[:, 3:6]], dim=1)
        ranges = (observations[:, -1, :128] * 8).clamp(0, 8)
        motion = perceived[:, 3:6].clone(); motion[:, 2] = 0
        speed = motion.norm(dim=1, keepdim=True)
        motion = motion / speed.clamp_min(1e-6)
        motion = torch.where(speed > .1, motion, torch.tensor([1., 0., 0.], device=motion.device))
        cone = motion @ self.short_directions.T >= self.stopping_cone_cosine
        ahead = ranges.masked_fill(~cone, torch.inf).min(1).values
        up = ranges.masked_fill(self.short_directions[:, 2][None] < .9396926, torch.inf).min(1).values
        down = ranges.masked_fill(self.short_directions[:, 2][None] > -.9396926, torch.inf).min(1).values
        return torch.cat([perceived, torch.stack([ahead, up, down], 1)], 1)


class ApproachContextPortalFeedbackPolicy(GuardedPortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = ApproachContextPortalNeuralFeatures
        PortalFeedbackPolicy.__init__(self, *args, **kwargs)


class RangeApproachContextPortalNeuralFeatures(ApproachContextPortalNeuralFeatures):
    """Use short neural distances to prevent approach inside the stand-off."""
    def forward(self, observations):
        base = super().forward(observations)
        center, _ = self.perception(observations)
        normal = self.normal(observations)
        goal = observations[:, -1, 256:259]
        goal = goal / goal.norm(dim=1, keepdim=True).clamp_min(1e-6)
        normal = torch.where((normal * goal).sum(1, keepdim=True) < 0, -normal, normal)
        longitudinal = (center[:, :3] * normal).sum(1, keepdim=True)
        transverse = center[:, :3] - normal * longitudinal
        ranges = (observations[:, -1, :128] * 8).clamp(0, 8)
        alignment = normal @ self.short_directions.T
        usable = (alignment > .9) & (ranges < 7.7) & (self.short_directions[:, 2].abs()[None] < .4)
        projected = (ranges * alignment).masked_fill(~usable, torch.nan)
        measured = torch.nanmedian(projected, dim=1).values[:, None]
        measured = torch.where(torch.isfinite(measured), measured, longitudinal)
        plane_distance = torch.minimum(measured, longitudinal)
        aligned = (transverse.norm(dim=1, keepdim=True) < .65) & (longitudinal < 3.)
        target = torch.where(aligned, center[:, :3] + 1.2 * normal,
                             transverse + normal * (plane_distance - 1.3))
        distance = (observations[:, -1, 259:260] * self.room_distance_scale).clamp_min(0)
        target = torch.where(distance < 2, goal * distance, target)
        return torch.cat([target, base[:, 3:]], dim=1)


class RangeApproachContextPortalFeedbackPolicy(GuardedPortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = RangeApproachContextPortalNeuralFeatures
        PortalFeedbackPolicy.__init__(self, *args, **kwargs)


def align_previous_panorama(observations):
    """Rotate the previous neural panorama using observed beacon bearings.

    Bearing change approximates camera yaw; translation also changes bearing,
    so this is not exact visual odometry. No world pose or fixed history age is
    read. Invalid startup history retains its zero panorama.
    """
    old, current = observations[:, -2, 256:258], observations[:, -1, 256:258]
    old_valid = old.norm(dim=1, keepdim=True) > 1e-6
    current_valid = current.norm(dim=1, keepdim=True) > 1e-6
    fallback = torch.tensor([1., 0.], dtype=old.dtype, device=old.device)
    old_safe = torch.where(old_valid, old, fallback)
    current_safe = torch.where(current_valid, current, fallback)
    delta = torch.atan2(old_safe[:, 1], old_safe[:, 0]) - torch.atan2(current_safe[:, 1], current_safe[:, 0])
    delta = torch.where((old_valid & current_valid).flatten(), delta, torch.zeros_like(delta))
    image = observations[:, -2, SENSORS:SENSORS + 1800].reshape(-1, 1, 25, 72)
    padded = torch.cat([image[:, :, :, -1:], image, image[:, :, :, :1]], 3)
    columns = (torch.arange(72, dtype=old.dtype, device=old.device)[None] + delta[:, None] * (72 / (2 * np.pi))) % 72 + 1
    gx = (columns * (2 / 73) - 1)[:, None].expand(-1, 25, -1)
    gy = torch.linspace(-1, 1, 25, dtype=old.dtype, device=old.device)[None, :, None].expand(len(old), -1, 72)
    grid = torch.stack([gx, gy], 3)
    warped = torch.nn.functional.grid_sample(padded, grid, mode='bilinear', padding_mode='border', align_corners=True)
    result = observations.clone()
    result[:, -2, SENSORS:SENSORS + 1800] = warped.flatten(1)
    return result


class AlignedApproachContextPortalNeuralFeatures(ApproachContextPortalNeuralFeatures):
    def perception(self, observations):
        return super().perception(align_previous_panorama(observations))

    def normal(self, observations):
        return super().normal(align_previous_panorama(observations))


class AlignedApproachContextPortalFeedbackPolicy(GuardedPortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = AlignedApproachContextPortalNeuralFeatures
        PortalFeedbackPolicy.__init__(self, *args, **kwargs)


def tube_stopping_spaces(values, velocity, short_directions, panorama):
    """Stopping distances inside the body trajectory, rather than a wide cone."""
    ranges = torch.cat([(values[:, :128] * 8).clamp(0, 8),
                        (values[:, SENSORS:SENSORS + 1800] * 24).clamp(0, 24)], 1)
    directions = torch.cat([short_directions, panorama], 0)
    points = ranges[:, :, None] * directions[None]
    motion = torch.cat([velocity[:, :2], torch.zeros_like(velocity[:, :1])], 1)
    norm = motion.norm(dim=1, keepdim=True)
    motion = motion / norm.clamp_min(1e-6)
    motion = torch.where(norm > .1, motion, torch.tensor([1., 0., 0.], device=motion.device))
    along = (points * motion[:, None]).sum(2)
    perpendicular = (points - along[:, :, None] * motion[:, None]).norm(dim=2)
    ahead = along.masked_fill((along <= 0) | (perpendicular > .28), torch.inf).min(1).values.clamp_max(24)
    vertical_tube = points[:, :, :2].norm(dim=2) < .28
    up = points[:, :, 2].masked_fill(~vertical_tube | (points[:, :, 2] <= 0), torch.inf).min(1).values.clamp_max(24)
    down = (-points[:, :, 2]).masked_fill(~vertical_tube | (points[:, :, 2] >= 0), torch.inf).min(1).values.clamp_max(24)
    return torch.stack([ahead, up, down], 1)


class TubeApproachContextPortalNeuralFeatures(ApproachContextPortalNeuralFeatures):
    def forward(self, observations):
        base = super().forward(observations)
        spaces = tube_stopping_spaces(observations[:, -1], base[:, 3:6], self.short_directions, self.directions)
        return torch.cat([base[:, :6], spaces], 1)


class TubeApproachContextPortalFeedbackPolicy(GuardedPortalFeedbackPolicy):
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = TubeApproachContextPortalNeuralFeatures
        PortalFeedbackPolicy.__init__(self, *args, **kwargs)
