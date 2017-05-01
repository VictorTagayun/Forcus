import cozmo
import asyncio
import time
import random
import Common.wocmath

# squared distance threshold for head motion distance for distraction judgement
DISTRACTION_DISTANCE2_THRS = 15000
# ignore slight head motion
MOTION_ERROR_THRS = 1000
UPDATING_FACTOR = 0.1
FORGIVE_THRS = 100
# grace number of distractions to level up angriness
ANGRY_SCALE = [0, 3, 6, 9, 99999]

WORDS = [["Hey", "Oh, no", "Huh"],
         ["Pay Attention", "Focus"],
         [],
         ["AAAAAAAAAAA", "OOOOOOOOOOO"]]

ANIMS = [["anim_reacttoblock_frustrated_01", "anim_speedtap_winhand_02", "anim_speedtap_winhand_03", "anim_memorymatch_failgame_player_01", "anim_memorymatch_solo_reacttopattern_03"],
         ["anim_speedtap_losehand_02", "anim_memorymatch_failhand_player_03", "anim_memorymatch_solo_reacttopattern_01"],
         ["anim_keepaway_losegame_03", "anim_rtpmemorymatch_no_02"],
         ["anim_speedtap_loseround_intensity01_01", "reacttoblock_triestoreach_01"]]

class Supervisor:
    def __init__(self, robot : cozmo.robot.Robot):
        self._facePosition = None
        self._robot = robot
        self._cozmoVoice = False
        self._distractionCount = 0
        self._faceMoved = False
        self._angryState = 0
        self._trackingFace = None
        self._forgiveness = 0

    # start staring at human
    async def startStare(self):
        await self._robot.play_anim("anim_meetcozmo_lookface_getin").wait_for_completed()

    # event handler to update observed face
    async def seeFacePosition(self, newPosition: cozmo.util.Position, face: cozmo.faces.Face):
        if self._trackingFace and self._trackingFace == face:
            if self._facePosition:
                # check face movement distance
                dist2 = Common.wocmath.distance2(newPosition, self._facePosition)
                self._facePosition = Common.wocmath.running_average_pos(self._facePosition, newPosition, UPDATING_FACTOR)

                if dist2 > DISTRACTION_DISTANCE2_THRS:
                    self._faceMoved = True
                else:
                    # face not moved much, start forgiving previous distraction
                    self._forgiveness += 1
                    
            else:
                self._facePosition = newPosition
        elif not self._trackingFace:
            self._trackingFace = face

    # called by face disappear event handler
    async def clearFace(self, face: cozmo.faces.Face):
        if self._trackingFace and self._trackingFace == face:
            self._trackingFace = None
            self._facePosition = None

    # called by face appear event handler
    async def seeFace(self, position: cozmo.util.Position, face: cozmo.faces.Face):
        if not self._trackingFace:
            self._trackinFace = face
            self._facePosition = position

    # called by forcus, check if face moved in previous short interval of time
    async def regularCheck(self):
        if self._forgiveness > FORGIVE_THRS:
            self._forgiveness = 0
            self._distractionCount -= 1
            if self._distractionCount < 0:
                self._distractionCount = 0
            print("Forgive, distraction remaining: ", self._distractionCount)
            await self.classifyAngriness()
            
        if self._faceMoved:
            print("Face moved!")
            await self.distractionReaction()
            self._facePosition = None
            self._faceMoved = False
            
    # find cooresponding angriness level
    async def classifyAngriness(self):
        for i in range(1, len(ANGRY_SCALE)):
            if self._distractionCount <  ANGRY_SCALE[i]:
                self._angryState = i - 1
                break
            
            
    # Cozmo reacts to human's distraction
    async def distractionReaction(self):
        # determine action based on angry state
        if not self._robot.has_in_progress_actions:
            self._distractionCount += 1
            await self.classifyAngriness()
            print("Angry lv ", self._angryState, ", distraction ", self._distractionCount)
            anim_i = random.randrange(len(ANIMS[self._angryState]))
            await self._robot.play_anim(ANIMS[self._angryState][anim_i]).wait_for_completed()
            await self.startStare()
            #self._cozmoVoice = not self._cozmoVoice
            #self._robot.say_text("Hey", use_cozmo_voice=self._cozmoVoice, in_parallel=False)
        
