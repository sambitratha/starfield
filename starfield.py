import pygame
import thread
import pygame.locals as locals
import time
import random
import math
import sys

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (127, 127, 127)
yellow = (255, 100, 100)
orange = (255, 165, 0)

gameConfig = {
    "width"       : 700,
    "height"      : 600,
    "gameWidth"   : 300,
    "gameHeight"  : 200,
    "lowMargin"   : 100,
    "upMargin"    : 100,
    "rows"        : 4,
    "cols"        : 6,
    "starCount"   : 50,
    "shipWidth"   : 35,
    "shipHeight"  : 35,
    "distance"    : 200,
    "shipColor"   : green,
    "gap"         : 15,
    "podColor"    : yellow,
    "bulletwidth" : 5,
    "bulletheight": 20,
    "bulletcolor" : red,
    "framev"      : 10,
    "maxpadleft"  : 100,
    "maxpadright" : 100
}

scorelist = {

    "rocket"    : 5,
    "ship"      : 3
}


displacement = (gameConfig["width"] - gameConfig["gameWidth"]) / 2
level = 1
score = 0

DISPLAYSURF = pygame.display.set_mode((gameConfig["width"], gameConfig["height"]), 0, 32)
pygame.display.set_caption('Space Invaders')
stars = []
fps = 5
fpsClock = pygame.time.Clock()
font = None
lastbullet = None

state = []
for i in range(gameConfig["rows"]):
    l = []
    for j in range(gameConfig["cols"]):
        l.append(1)
    state.append(l)

gamestate = {

    "state"     : state,
    "lives"     : 3,
    "podx"      : gameConfig["width"]/2,
    "pody"      : gameConfig["upMargin"] + gameConfig["gameHeight"] + gameConfig["distance"],
    "podv"      : 6,
    "bulletv"   : 8
}

bulletcolors = [white, orange, red, blue]

lastship = []
for _ in range(gameConfig["cols"]):
    lastship.append(gameConfig["rows"] - 1)

class Star:
    def __init__(self):
        self.x = random.randint(1, gameConfig["width"])
        self.y = random.randint(1, gameConfig["height"]/3)
        self.velocity = random.randint(1, 3)
        self.radius = random.randint(1, 2)

class Bullet:
    def __init__(self,x, y):
        self.x = x
        self.y = y
        self.width = gameConfig["bulletwidth"]
        self.height = gameConfig["bulletheight"]

class Rocket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velx = 4
        self.speed = 4
        self.vely = 10
        self.radius = 10
        self.level = random.randint(1, level)
        self.color = bulletcolors[self.level]
        self.speed += self.level - 1
        self.velx += self.level - 1
        self.vely += self.level - 1


bullets = []
rockets = []


def StarFieldAnimationInit():
    global stars
    for i in range(gameConfig["starCount"]):
        newstar = Star()
        stars.append(newstar)
    pass

def StarFieldAnimationUpdate():
    global stars
    for i in range(len(stars)):
        stars[i].y += float(stars[i].velocity) * (30.0/1000)
    
        if stars[i].y > gameConfig["height"]:
            stars[i].y = random.randint(1, gameConfig["height"]/5)

def StarFieldAnimationDraw(display):
    for star in stars:
        pygame.draw.circle(display, white, (int(star.x) , int(star.y)), star.radius)


def WelcomeScreen(display):
    StarFieldAnimationInit()
    while True:
        display.fill(black)

        welcomeX = (gameConfig["width"]) / 2
        welcomeY = gameConfig["height"] / 2
        tx, tr = getStringObject("Press space to play" , welcomeX, welcomeY, yellow)
        display.blit(tx, tr)

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == locals.KEYUP and event.key == locals.K_SPACE:
                return
            
        StarFieldAnimationUpdate()
        StarFieldAnimationDraw(display)

        pygame.display.update()
        fpsClock.tick()



def MainGame(display):
    global gameConfig, gamestate, bullets, level, lastbullet, lastship
    left = False
    right = False 
    while True:
        display.fill(black)
        if gamestate["lives"] <= 0:
            return

        if gamestate["state"] == [[0] * gameConfig["cols"]] * gameConfig["rows"]:
            level += 1
            gamestate["state"] = []
            state = []
            for i in range(gameConfig["rows"]):
                l = []
                for j in range(gameConfig["cols"]):
                    l.append(1)
                state.append(l)
            gamestate["state"] = state
            lastship = []
            for _ in range(gameConfig["cols"]):
                lastship.append(gameConfig["rows"] - 1)
            

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                return


            if event.type == locals.KEYDOWN and event.key == locals.K_LEFT:
                left = True

            if event.type == locals.KEYUP:
                if event.key == locals.K_LEFT:
                    left = False
                if event.key == locals.K_RIGHT:
                    right = False

            if event.type == locals.KEYDOWN and event.key == locals.K_RIGHT:
                right = True

            if event.type == locals.KEYDOWN and event.key == locals.K_SPACE:
                cur_time = time.time()
                if lastbullet == None or (cur_time - lastbullet) * 1000 > 600:
                    newbullet = Bullet(gamestate["podx"] + gameConfig["shipWidth"]/2, gamestate["pody"])
                    bullets.append(newbullet)
                    lastbullet = cur_time


        if left:
            gamestate["podx"] -= (float(gamestate["podv"])* (30.0/1000))

        if right:
            gamestate["podx"] += (float(gamestate["podv"])* (30.0/1000))


        GenerateRocket()
        UpdateRocket()

        CheckForCollison()


        StarFieldAnimationUpdate()
        StarFieldAnimationDraw(display)
        DrawRockets(display)
        DrawShips(display)
        DrawBullets(display)
        ShowScore(display)
        pygame.display.update()


def GenerateRocket():
    global rockets
    ranint = random.randint(1, 1000)
    rocket = None
    if len(rockets) == 3:
        return None
    if ranint % 1 == 0:
        rocket = Rocket(random.randint(1, gameConfig["width"]), 0)
        rockets.append(rocket)
    return  None

def UpdateRocket():
    global rockets
    for rocket in rockets:
        if rocket.y >= gameConfig["height"]:
            rockets.pop(rockets.index(rocket))
        else:
            if rocket.x >= gamestate["podx"]:
                rocket.velx = - rocket.speed
            else:
                rocket.velx = rocket.speed

            rocket.x += float(rocket.velx) * (30.0/1000)
            rocket.y += float(rocket.vely) * (30.0/1000)

def CheckForCollison():
    global bullets, lastship, gamestate, rockets, score
    for bullet in bullets:
        for col in range(len(lastship)):
            if lastship[col] < 0:
                continue
            xcord = displacement+ col * (gameConfig["shipWidth"] + gameConfig["gap"])
            ymargin = (gameConfig["height"] - gameConfig["lowMargin"] - gameConfig["distance"] - gameConfig["gameHeight"])
            ycord = ymargin + lastship[col] * (gameConfig["shipHeight"] + gameConfig["gap"])
            width =  gameConfig["shipWidth"]
            height = gameConfig["shipHeight"]

            #check for collison between (rocket , bullet) and (bullet , ship)
            try:
                if bullet.x < xcord + width and bullet.x + bullet.width > xcord:
                    if bullet.y <= ycord + height:
                        gamestate["state"][lastship[col]][col] = 0
                        bullets.pop(bullets.index(bullet))
                        lastship[col] -= 1
                        score += scorelist["ship"]

                else:
                    for rocket in rockets:
                        if bullet.x < rocket.x + rocket.radius and bullet.x + bullet.width > rocket.x - rocket.radius:
                            if bullet.y < rocket.y + rocket.radius and bullet.y + bullet.height > rocket.y - rocket.radius:
                                bullets.pop(bullets.index(bullet))
                                rockets.pop(rockets.index(rocket))
                                score += scorelist["rocket"]
                                break
            except:
                pass


    #check for collison with the main ship and rockets
    for rocket in rockets:
        rx, ry = rocket.x , rocket.y
        radius = rocket.radius
        sx, sy = gamestate["podx"], gamestate["pody"]
        width, height = gameConfig["shipWidth"], gameConfig["shipHeight"]
        if rx - radius < sx + width and rx + radius > sx:
            if ry - radius > sy and ry + radius < sy + height:
                #collison has occured
                gamestate["lives"] -= 1
                rockets.pop(rockets.index(rocket))


def DrawRockets(display):
    for rocket in rockets:
        pygame.draw.circle(display, rocket.color, (int(rocket.x) , int(rocket.y)) , rocket.radius)

def DrawBullets(display):
    global bullets
    for bullet in bullets:
        if bullet.y < 0 or bullet.y > gameConfig["height"]:
            bullets.pop(bullets.index(bullet))
        else:
            pygame.draw.rect(display, gameConfig["bulletcolor"], (bullet.x, bullet.y, gameConfig["bulletwidth"], gameConfig["bulletheight"]))
            bullet.y -= (float(gamestate["bulletv"]) * (30.0/1000))


def DrawShips(display):
    global gameConfig, displacement
    xmargin = (gameConfig["width"] - gameConfig["gameWidth"])/2
    ymargin = (gameConfig["height"] - gameConfig["lowMargin"] - gameConfig["distance"] - gameConfig["gameHeight"])
    if displacement < gameConfig["maxpadleft"]:
        gameConfig["framev"] *= -1
    elif displacement > gameConfig["width"] - gameConfig["gameWidth"] - gameConfig["maxpadright"]:
        gameConfig["framev"] *= -1

    displacement += (float(gameConfig["framev"]) * (30.0/ 1000))

    for i in range(gameConfig["rows"]):
        for j in range(gameConfig["cols"]):
            if gamestate["state"][i][j] == 0:
                continue
            centerx = displacement + j * (gameConfig["shipWidth"] + gameConfig["gap"])
            centery = ymargin + i * (gameConfig["shipHeight"] + gameConfig["gap"])
            pygame.draw.rect(display, gameConfig["shipColor"], (centerx, centery, gameConfig["shipWidth"], gameConfig["shipHeight"]))

    pygame.draw.rect(display, gameConfig["podColor"], (int(gamestate["podx"]), int(gamestate["pody"]), gameConfig["shipWidth"], gameConfig["shipHeight"]))
    pass


def getStringObject(s,centerx,centery, color = white):
    textObj = font.render(s,True, color)
    textRect = textObj.get_rect()
    textRect.center = (centerx, centery)
    return textObj , textRect


def ShowScore(display):
    livesx = gameConfig["width"]/6
    livesy = 50
    tx, tr = getStringObject("lives : " + str(gamestate["lives"]), livesx, livesy)
    display.blit(tx, tr)
    scorecardx = (gameConfig["width"] * 5) / 6
    scorecardy = livesy
    tx, tr = getStringObject("score: " + str(score) , scorecardx, scorecardy)
    display.blit(tx, tr)

def GameOver(display):
    while 2 > 1:
        display.fill(black)

        gameoverX = (gameConfig["width"]) / 2
        gameoverY = 150
        tx, tr = getStringObject("Game Over" , gameoverX, gameoverY, white)
        display.blit(tx, tr)

        scorecardx = (gameConfig["width"]) / 2
        scorecardy = 250
        tx, tr = getStringObject("Score: " + str(score) , scorecardx, scorecardy, white)
        display.blit(tx, tr)
        
        retryX = (gameConfig["width"]) / 2
        retryY = 350
        tx, tr = getStringObject("Press R for retry" , retryX, retryY, yellow)
        display.blit(tx, tr)

        quitX = (gameConfig["width"]) / 2
        quitY = 450
        tx, tr = getStringObject("Press Q to exit" , quitX, quitY, yellow)
        display.blit(tx, tr)

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                return
            if event.type == locals.KEYDOWN and event.key == locals.K_r:
            	print "r pressed"
            	reset()
            	play(display)
            if event.type == locals.KEYDOWN and event.key == locals.K_q:
            	sys.exit()

        pygame.display.update()



def reset():
	global gameConfig, gamestate, rockets, bullets, displacement, lastship, score, lastbullet, level
	gameConfig["framev"] = 10
	state = []
	for i in range(gameConfig["rows"]):
		l = []
		for j in range(gameConfig["cols"]):
			l.append(1)
		state.append(l)

	gamestate = {

	    "state"     : state,
	    "lives"     : 3,
	    "podx"      : gameConfig["width"]/2,
	    "pody"      : gameConfig["upMargin"] + gameConfig["gameHeight"] + gameConfig["distance"],
	    "podv"      : 6,
	    "bulletv"   : 8
	}
	bullets = []
	rockets = []
	displacement = (gameConfig["width"] - gameConfig["gameWidth"]) / 2
	lastship = []
	for _ in range(gameConfig["cols"]):
		lastship.append(gameConfig["rows"] - 1)
	score = 0
	level = 1
	lastbullet = None


def play(display):
	MainGame(display)
	GameOver(display)


if __name__ == "__main__":
    pygame.init()
    font = pygame.font.Font("EraserRegular.ttf",20)
    WelcomeScreen(DISPLAYSURF)
    play(DISPLAYSURF)






