"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import numpy as np
from random import randint
def get_pos(b_pos, last_b_pos, bricks, hbricks):
    AREA_WIDTH = 200
    AREA_HEIGHT = 500
    PLATE_YPOS = 400
    BRICK_WIDTH = 25
    BRICK_HEIGHT = 10
    BALL_R = 5
    
    b_v = b_pos - last_b_pos
    '''
    while(b_pos[1] < PLATE_YPOS):
        b_pos += b_v
        
        Collide = collideState(b_pos, b_v, bricks, hbricks)
        # area cut
        if b_pos[0] < 0:
            b_pos[0] = 0
            b_v[0] = -b_v[0]
        elif b_pos[0] + BALL_R > AREA_WIDTH:
            b_pos[0] = AREA_WIDTH - BALL_R
            b_v[0] = -b_v[0]
        elif b_pos[1] < 0:
            b_pos[1] = 0
            b_v[1] = -b_v[1]
        # collide 
        for bick in bricks:
            Collide = collideState(b_pos, b_v, brick)
            if (Collide[0]):
    '''
def collideState(b_pos, b_v, bricks, hbricks):
    AREA_WIDTH = 200
    BRICK_WIDTH = 25
    BRICK_HEIGHT = 10
    R = 5
    isCollide = False
    
    last_b_pos = b_pos - b_v
    bricks += hbricks
    
    for brick in bricks:
        if (np.shape(brick)[0] == 0):
            break
        if b_pos[0] <= 0:
            return True, "L"
        elif b_pos[0] + R >= AREA_WIDTH:
            return True, "R"
        elif b_pos[1] <= 0:
            return True, "U"
        # 球切入邊界判定
        if (brick[1] <= b_pos[1] <= brick[1] + BRICK_HEIGHT):  # 球上邊界判定
            # 球左右邊界判定
            if (brick[0] <= b_pos[0] <= brick[0] + BRICK_WIDTH):
                isCollide = True
            elif (brick[0] <= b_pos[0] + R <= brick[0] + BRICK_WIDTH):
                isCollide = True
        elif (brick[1] <= b_pos[1] + R <= brick[1] + BRICK_HEIGHT):  # 球下邊界判定
            # 球左右邊界判定
            if (brick[0] <= b_pos[0] <= brick[0] + BRICK_WIDTH):
                isCollide = True
            elif (brick[0] <= b_pos[0] + R <= brick[0] + BRICK_WIDTH):
                isCollide = True
        # 確認碰撞邊界: 分別確認球移動路徑切過哪個磚塊邊界
        if (b_v[0] < 0 and isCollide): # 球速朝左
            x_dif = (brick[0] + BRICK_WIDTH) - (last_b_pos[0])
            xfitR_t = x_dif / b_v[0]
            y_xfitR = last_b_pos[1] + b_v[1] * xfitR_t
            if (brick[1] + BRICK_HEIGHT < y_xfitR and b_v[1] < 0):
                return isCollide, "U"
            elif (brick[1] > y_xfitR and b_v[1] > 0):
                return isCollide, "D"
            else:
                return isCollide, "L"
        elif (b_v[0] > 0 and isCollide): # 球速朝右
            x_dif = (brick[0]) - (last_b_pos[0])
            xfitL_t = x_dif / b_v[0]
            y_xfitL = last_b_pos[1] + b_v[1] * xfitL_t
            if (brick[1] + BRICK_HEIGHT < y_xfitL and b_v[1] < 0):
                return isCollide, "U"
            elif (brick[1] > y_xfitL and b_v[1] > 0):
                return isCollide, "D"
            else:
                return isCollide, "R"
    return isCollide, "N"
def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    AREA_WIDTH = 200
    AREA_HIGHT = 500
    PLATE_WIDTH = 40
    PLATE_HWIDTH = int(PLATE_WIDTH / 2)
    PLATE_QWIDTH = int(PLATE_HWIDTH / 2)
    PLATE_YPOS = 400
    BALL_R = 5
    
    v = np.zeros(2, dtype=int)
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    
    flag = True
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        if flag:
            #print(scene_info)
            bpre_pos = scene_info.ball
            print(scene_info.bricks)
            print(scene_info.hard_bricks)
            flag = False
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue
        
        # 3.3. Put the code here to handle the scene information
        pcur_pos = np.array(scene_info.platform)
        
        if ball_served:
            # calcutlate ball's velocity
            bpre_pos = bcur_pos
            bcur_pos = np.array(scene_info.ball)
            v = bcur_pos - bpre_pos
            
            print(collideState(bcur_pos, v, scene_info.bricks, scene_info.hard_bricks))
            # figure out where will the ball touch the plate
            if v[0] !=0 and v[1]>0:
                fall_time = (PLATE_YPOS - bcur_pos[1] - BALL_R) / v[1]
                x_travel = fall_time * v[0]
                fold_times = int((np.abs(bcur_pos[0] + x_travel)) / AREA_WIDTH)
                
                fall_x = int(np.abs(bcur_pos[0] + x_travel)) % AREA_WIDTH
                if (fold_times % 2 == 0):
                    fall_x = fall_x
                else:
                    fall_x = AREA_WIDTH - fall_x

            else:
                fall_x = AREA_WIDTH / 2
            
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            if randint(0,1) == 1:
                comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
            ball_served = True
            bcur_pos = scene_info.ball
        elif (v[1] > 0):
            # move plate pos base on estimate fall pos at plate's: left, middle, right 
            if pcur_pos[0] + PLATE_QWIDTH < fall_x < pcur_pos[0] + PLATE_QWIDTH * 3:
                if np.abs(bcur_pos[1] - pcur_pos[1]) <= 2 * BALL_R:
                    if randint(0,1)==0: comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    else: comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            elif pcur_pos[0] + PLATE_HWIDTH < fall_x:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
