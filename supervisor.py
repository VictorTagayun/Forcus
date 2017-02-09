import cozmo
import asyncio

DISTRACTION_DISTANCE_THRS = 30000
MOTION_ERROR_THRS = 1000


class Supervisor:
    def __init__(self, robot : cozmo.robot.Robot):
        self._facePosition = None
        self._robot = robot
        self._cozmoVoice = False

    async def startStare(self):
        self._robot.play_anim("anim_meetcozmo_lookface_getin")

    async def seeFacePosition(self, newPosition: cozmo.util.Vector3):
        if self._facePosition:
            #TODO: check face movement distance
            dist2 = self.distance2(newPosition, self._facePosition)
            if dist2 > MOTION_ERROR_THRS:
                self._facePosition = newPosition
            if dist2 > DISTRACTION_DISTANCE_THRS:
                print("Face moved!")
                print(dist2)
                if not self._robot.has_in_progress_actions:
                    self._cozmoVoice = not self._cozmoVoice
                    self._robot.say_text("Hey", use_cozmo_voice=self._cozmoVoice, in_parallel=False)
        else:
            self._facePosition = newPosition
        

    def distance2(self, pos1: cozmo.util.Vector3, pos2: cozmo.util.Vector3):
        xx = pos1.x - pos2.x
        yy = pos1.y - pos2.y
        zz = pos1.z - pos2.z
        return xx * xx + yy * yy + zz * zz
