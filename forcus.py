# Forcus stands for Forced Focus
import cozmo
import asyncio
from supervisor import Supervisor
from Common.woc import WOC

FOCUS_TIME = 600
SEARCH_FACE_TIMEOUT = 5
FRAME_DROP = 5

class ForcedFocus(WOC):

    def __init__(self, focus_time, *a, **kw):
        WOC.__init__(self)
        self.focus_time = focus_time
        self.curr_time = 0
        self._face = None
        self._prevPose = None
        self._supervisor = None

        cozmo.setup_basic_logging()
        cozmo.connect_with_tkviewer(self.run)

    async def run(self, coz_conn: cozmo.conn.CozmoConnection):
        robot = await coz_conn.wait_for_robot()
        self._supervisor = Supervisor(robot)
        robot.move_lift(-3)
        # robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE)
        robot.world.add_event_handler(cozmo.faces.EvtFaceObserved, self.onFaceObserved)
        robot.world.add_event_handler(cozmo.faces.EvtFaceAppeared, self.onFaceAppeared)
        robot.world.add_event_handler(cozmo.faces.EvtFaceDisappeared, self.onFaceDisappeared)
        await self._supervisor.startStare()
        
        while not self.exit_flag:
            if self._face and self._face.is_visible:
                #self._face
                pass
            else:
                try:
                    self._face = await robot.world.wait_for_observed_face(timeout=SEARCH_FACE_TIMEOUT)
                except asyncio.TimeoutError:
                    self.curr_time += SEARCH_FACE_TIMEOUT
                    print("Fail to find a face")
            
            await asyncio.sleep(0.5)
            await self._supervisor.regularCheck()
            self.curr_time += 0.5
            if self.curr_time > self.focus_time:
                break

    async def onFaceObserved(self, evt: cozmo.faces.EvtFaceObserved, obj=None, **kwargs):
        poseDiff = None
        #print("-----------current-------")
        #print(evt.pose)
        if self._prevPose:
            poseDiff = evt.pose - self._prevPose
            positionDiff = evt.pose.position - self._prevPose.position
        self._prevPose = evt.pose
        
        if self._supervisor:
            await self._supervisor.seeFacePosition(evt.pose.position, evt.face)
        #print(obj.pose)

    async def onFaceAppeared(self, evt: cozmo.faces.EvtFaceAppeared, obj=None, **kwargs):
        await self._supervisor.seeFace(evt.pose.position, evt.face)

    async def onFaceDisappeared(self, evt: cozmo.faces.EvtFaceDisappeared, obj=None, **kwargs):
        await self._supervisor.clearFace(evt.face)

if __name__ == '__main__':
    ForcedFocus(FOCUS_TIME)
