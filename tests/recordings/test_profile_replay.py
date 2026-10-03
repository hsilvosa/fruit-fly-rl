import numpy as np
from fly_rl.simulation.world import FlightWorld
from fly_rl.recordings.recording import FlightRecorder
from fly_rl.recordings.replay import ReplayEnv


def test_profiled_archive_replays_actual_size_profile_and_flight_state(tmp_path):
    w = FlightWorld(10, 'dense', dynamics='coordinated', map_profile='maze')
    recorder = FlightRecorder(tmp_path, {'dt': .05, 'dataset': {'annotated_neurons': 16, 'edges': 16}})
    recorder.event('room', 0, {'room_id': 0, 'seed': 10, 'size': w.room, 'initial_state': w.snapshot()})
    before, sensors = w.snapshot(), w.observe()
    action = np.array([.5, 0, .1, 0], dtype=np.float32)
    obs, reward, done, truncated, info = w.step(action)
    info.update(next_sensors=obs, next_brain_features=np.zeros(256, dtype=np.float32))
    recorder.transition(1, 0, sensors, np.zeros(256, dtype=np.float32), action, before, info, reward)
    recorder.close()
    replay = ReplayEnv(recorder.path)
    assert replay.worlds[0].map_profile == w.map_profile
    assert np.array_equal(replay.worlds[0].room, [64, 64, 20])
    assert replay.worlds[0].mode == 'dense' and replay.worlds[0].dynamics == 'coordinated'
    assert replay.worlds[0].episode_limit == w.episode_limit
    replay.step(None)
    assert np.array_equal(replay.worlds[0].position, w.position) and replay.finished
