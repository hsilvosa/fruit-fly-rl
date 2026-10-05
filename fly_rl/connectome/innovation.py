"""Diagnostic stimulus reconstruction from full recurrent neuron activity.

This readout explicitly subtracts recurrent drive. It is an information upper
bound, not evidence of a useful biological computation or reservoir advantage.
No raw sensor values are used by reconstruct_activity.
"""
import numpy as np
import torch
from scipy import sparse
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.sensors import SENSOR_V6

INNOVATION_READOUT = 'neural-innovation-least-squares-v1'
WHITENED_READOUT = 'neural-projection-whitened-innovation-v1'


class InnovationBrain(Brain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.sensor_version != SENSOR_V6:
            raise ValueError('Innovation diagnostic requires the v6 projection')
        self.feature_count = self.sensor_count
        self.readout_version = INNOVATION_READOUT
        self.model_spec += ':' + INNOVATION_READOUT
        rows = np.repeat(np.arange(self.n), 4)
        columns = np.column_stack([self.input_index.cpu().numpy(), self.fan_index.cpu().numpy()]).ravel()
        weights = np.column_stack([.5 * self.input_sign.cpu().numpy(), .25 * self.fan_sign.cpu().numpy()]).ravel()
        projection = sparse.coo_matrix((weights, (rows, columns)), shape=(self.n, self.sensor_count)).tocsr()
        norm = np.sqrt(np.asarray(projection.power(2).sum(0)).ravel())
        if (norm == 0).any():
            raise ValueError('Stimulus reconstruction requires every projection column')
        normalized = (projection @ sparse.diags(1 / norm)).tocsr()
        gram = (normalized.T @ normalized).toarray().astype(np.float32)
        # The ridge is numerical stabilization; the reconstruction error is
        # measured rather than claimed to be mathematically exact.
        gram.flat[::self.sensor_count + 1] += 1e-6
        self.factor = torch.linalg.cholesky(torch.tensor(gram, device=self.device))
        self.norm = torch.tensor(norm, dtype=torch.float32, device=self.device)
        transpose = normalized.T.tocsr()
        self.projection_transpose = torch.sparse_csr_tensor(
            torch.tensor(transpose.indptr, dtype=torch.int64, device=self.device),
            torch.tensor(transpose.indices, dtype=torch.int64, device=self.device),
            torch.tensor(transpose.data, dtype=torch.float32, device=self.device),
            size=transpose.shape)
        self.centering_drive = .25 * (self.fan_center * self.fan_sign).sum(1)

    @torch.no_grad()
    def project_activity(self, previous, current, subtract_recurrence):
        if previous.shape != self.state.shape or current.shape != self.state.shape:
            raise ValueError('Full previous and current neuron states are required')
        activation = (2 * current - previous).clamp(-1 + 1e-6, 1 - 1e-6)
        drive = torch.atanh(activation)
        if subtract_recurrence:
            drive -= torch.sparse.mm(self.matrix, previous)
        drive += self.centering_drive[:, None]
        rhs = torch.sparse.mm(self.projection_transpose, drive)
        result = torch.cholesky_solve(rhs, self.factor) / self.norm[:, None]
        return result.T.contiguous().cpu().numpy()

    @torch.no_grad()
    def reconstruct_activity(self, previous, current):
        return self.project_activity(previous, current, subtract_recurrence=True)

    @torch.no_grad()
    def step(self, sensors):
        previous = self.state.clone()
        super().step(sensors)
        return self.reconstruct_activity(previous, self.state)


class WhitenedActivityBrain(InnovationBrain):
    """Remove projection cross-talk while retaining projected recurrent drive.

    The least-squares features contain A^+ W previous_state as well as current
    stimulus drive. This is not the recurrence-canceling information bound.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readout_version = WHITENED_READOUT
        self.model_spec = self.model_spec.replace(INNOVATION_READOUT, WHITENED_READOUT)

    @torch.no_grad()
    def reconstruct_activity(self, previous, current):
        return self.project_activity(previous, current, subtract_recurrence=False)


CONTRAST_READOUT = 'neural-projection-contrast-recurrence005-v1'


class ContrastActivityBrain(InnovationBrain):
    """Reduce recurrent interference in sensory coordinates to five percent.

    All neurons and edges still advance. This engineered readout subtracts
    95 percent of recurrent drive; it is not a biological model or advantage.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readout_version = CONTRAST_READOUT
        self.model_spec = self.model_spec.replace(INNOVATION_READOUT, CONTRAST_READOUT)

    @torch.no_grad()
    def reconstruct_activity(self, previous, current):
        if previous.shape != self.state.shape or current.shape != self.state.shape:
            raise ValueError('Full previous and current neuron states are required')
        drive = torch.atanh((2 * current - previous).clamp(-1 + 1e-6, 1 - 1e-6))
        drive -= .95 * torch.sparse.mm(self.matrix, previous)
        drive += self.centering_drive[:, None]
        rhs = torch.sparse.mm(self.projection_transpose, drive)
        return (torch.cholesky_solve(rhs, self.factor) / self.norm[:, None]).T.contiguous().cpu().numpy()


MOTION_STABLE_READOUT = 'neural-projection-motion-stable-visual005-v1'


class MotionStableActivityBrain(InnovationBrain):
    """Cancel projected recurrence in base channels; retain it in panorama.

    This engineered readout decodes the full neuronal drive twice using the
    fixed projection. It reads no sensor values during reconstruction. Synthetic base distance, target and motion channels support odometry;
    panorama channels retain five
    percent projected recurrence. It is not a biological sensory mechanism.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readout_version = MOTION_STABLE_READOUT
        self.model_spec = self.model_spec.replace(INNOVATION_READOUT, MOTION_STABLE_READOUT)
        self.recurrent_gain = torch.full((self.sensor_count, 1), .05, device=self.device)
        self.recurrent_gain[:269] = 0

    @torch.no_grad()
    def reconstruct_activity(self, previous, current):
        if previous.shape != self.state.shape or current.shape != self.state.shape:
            raise ValueError('Full previous and current neuron states are required')
        drive = torch.atanh((2 * current - previous).clamp(-1 + 1e-6, 1 - 1e-6))
        drive += self.centering_drive[:, None]
        recurrent = torch.sparse.mm(self.matrix, previous)
        rhs = torch.sparse.mm(self.projection_transpose, torch.cat([drive - recurrent, recurrent], dim=1))
        decoded = torch.cholesky_solve(rhs, self.factor) / self.norm[:, None]
        clean, context = decoded.chunk(2, dim=1)
        result = clean + self.recurrent_gain * context
        return result.T.contiguous().cpu().numpy()
