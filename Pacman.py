import pygame, sys, copy, time, heapq
from pygame.locals import *

#http://www.redblobgames.com/pathfinding/a-star/implementation.html
class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class Game():
    def __init__(self):
        pygame.init()
        
        #debug tools#
        self.drawTargetTiles = 1
        #############
         
        tileSize    = 24
        self.screen = pygame.display.set_mode((1024, 724))
        self.clock  = pygame.time.Clock()
        
        self.scatterTimer = 0                    
        self.pelletsCollected = 0
        self.font = pygame.font.Font(None, 36)

        #build level
        self.level = Level()
                
        self.levelCoords = copy.deepcopy(self.level.grid)
        self.blockS = pygame.sprite.Group()

        self.pellet  = Pellet((200, 200))
        self.pelletS = pygame.sprite.RenderPlain((self.pellet))
        

        self.walls = pygame.sprite.Group()
        for row in range(len(self.level.grid)):
            for column in range(len(self.level.grid[1])):
                if self.level.grid[row][column] == 1:
                    block = Block(( 25 + (column*tileSize), 25 + (row*tileSize)))
                    self.blockS.add(pygame.sprite.RenderPlain((block)))
                else:
                   self.levelCoords[row][column] = ( 25 + (column*tileSize), 25 + (row*tileSize))
                   if self.level.grid[row][column] == 0:
                       pellet = Pellet(( 25 + (column*tileSize), 25 + (row*tileSize)))
                       self.pelletS.add(pygame.sprite.RenderPlain((pellet)))

        self.gridLength = len(self.levelCoords[0]) - 1
        self.gridHeight = len(self.levelCoords) - 1
        
        self.totalPellets = len(self.pelletS)

        #create and spawn player

        spawn = self.levelCoords[21][14]

        self.pacman  = Pacman(spawn)
        self.pacmanS = pygame.sprite.RenderPlain((self.pacman))

        #create ghosts
        self.blinky = Ghost(self.levelCoords[13][13], 0)
        self.inky   = Ghost(self.levelCoords[14][13], 1)
        self.pinky  = Ghost(self.levelCoords[13][14], 2)
        self.clyde  = Ghost(self.levelCoords[14][14], 3)
        
        self.ghostS   = pygame.sprite.RenderPlain((self.blinky))
        self.ghostS.add(pygame.sprite.RenderPlain((self.inky)))      
        self.ghostS.add(pygame.sprite.RenderPlain((self.pinky)))      
        self.ghostS.add(pygame.sprite.RenderPlain((self.clyde)))

    def mainLoop(self):
        running = True
        self.startTime = time.clock()
        self.pinky.canMove = 1
        
        while running:
            #INPUT
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if not hasattr(event, 'key'): continue
                if event.key == K_ESCAPE: running = False
                
                if event.key == K_RIGHT: self.pacman.kR = 2
                if event.key == K_LEFT:  self.pacman.kL = 2
                if event.key == K_UP:    self.pacman.kU = 2
                if event.key == K_DOWN:  self.pacman.kD = 2

            #UPDATE
            pelletCollisions = pygame.sprite.spritecollide(self.pacman, self.pelletS, True)
            for pellet in pelletCollisions:
                self.pelletsCollected += 1
                
            self.pacman.update()
            
            self.blinky.update()
            self.inky.update()
            self.pinky.update()
            self.clyde.update()

            #Ghosts leaving house logic
            curTime = time.clock()
            timePassed = int(curTime - self.startTime)
            if not self.blinky.canMove:
                if timePassed >= 3: self.blinky.canMove = 1
            if not self.inky.canMove:
                if self.pelletsCollected == 30: self.inky.canMove = 1
            if not self.clyde.canMove:   
                if self.pelletsCollected != 0:
                    percentCollected = (self.pelletsCollected / float(self.totalPellets)) * 100
                    if percentCollected >= 20: self.clyde.canMove = 1
                    
            #Scatter mode
            if timePassed == 25 or timePassed == 60 or timePassed == 105:
                self.blinky.scatter = 1
                self.inky.scatter   = 1
                self.pinky.scatter  = 1
                self.clyde.scatter  = 1

            if timePassed == 35 or timePassed == 70 or timePassed == 115:
                self.blinky.scatter = 0
                self.inky.scatter   = 0
                self.pinky.scatter  = 0
                self.clyde.scatter  = 0

            #RENDER
            self.screen.fill((0, 0, 0))
            
            self.pacmanS.draw(self.screen)
            self.pelletS.draw(self.screen)
            self.blockS.draw(self.screen) 
            self.ghostS.draw(self.screen)

            #UI
            text = self.font.render("Score %s" %(self.pelletsCollected * 100), 1, (255, 255, 255))
            textpos = text.get_rect(left=self.screen.get_width() - 300)
            textpos.move_ip(0, 20)
            self.screen.blit(text, textpos)
            
            textpos.move_ip(0, 50)
            y, x = self.pacman.gridLocation
            grid = [x, y]
            text = self.font.render("Pacman position %s" %str(grid).strip('[]'), 1, (255, 255, 255))
            self.screen.blit(text, textpos)
            
            textpos.move_ip(0, 50)
            y, x = self.blinky.targetTile
            grid = [x, y]
            text = self.font.render("Blinky target %s" %str(grid).strip('[]'), 1, (255, 255, 255))
            self.screen.blit(text, textpos)
            if self.drawTargetTiles: pygame.draw.rect(self.screen, (255, 0, 0), (5 + (x * 24), 5 + (y * 24), 10, 10))

            textpos.move_ip(0, 50)
            y, x = self.pinky.targetTile
            grid = [x, y]
            text = self.font.render("Pinky target %s" %str(grid).strip('[]'), 1, (255, 255, 255))
            self.screen.blit(text, textpos)
            if self.drawTargetTiles: pygame.draw.rect(self.screen, (255, 153, 255), (5 + (x * 24), 5 + (y * 24), 10, 10))

            textpos.move_ip(0, 50)
            y, x = self.inky.targetTile
            grid = [x, y]
            text = self.font.render("Inky target %s" %str(grid).strip('[]'), 1, (255, 255, 255))
            self.screen.blit(text, textpos)
            if self.drawTargetTiles: pygame.draw.rect(self.screen, (0, 0, 255), (5 + (x * 24), 5 + (y * 24), 10, 10))

            textpos.move_ip(0, 50)
            y, x = self.clyde.targetTile
            grid = [x, y]
            text = self.font.render("Clyde target %s" %str(grid).strip('[]'), 1, (255, 255, 255))
            self.screen.blit(text, textpos)
            if self.drawTargetTiles: pygame.draw.rect(self.screen, (255, 255, 0), (5 + (x * 24), 5 + (y * 24), 10, 10))

            pygame.display.flip()
            
        pygame.quit()

class Level():  #0 = pellet #1 = wall #2 = nothing
    def __init__(self):
        self.weights = {}
        self.walls = []
        self.intersections = []
        self.grid  = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 2, 2, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],             
                 [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1], 
                 [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1], 
                 [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1], 
                 [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                 [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        self.intersections.append((14,14))
        self.intersections.append((10,14))
        self.intersections.append((10,13))
        for row in range(len(self.grid)):
            for column in range(len(self.grid[1])):
                if self.grid[row][column] == 1:
                    self.walls.append((row, column))
                count = 0
                if self.grid[row][column] == 0:
                    if self.grid[row-1][column] == 0 or self.grid[row-1][column] == 2:
                        count += 1
                    elif self.grid[row+1][column] == 0 or self.grid[row+1][column] == 2:
                        count += 1
                    if self.grid[row][column-1] == 0 or self.grid[row][column-1] == 2:
                        count += 1
                    elif self.grid[row][column+1] == 0 or self.grid[row][column+1] == 2:
                        count += 1

                if count >= 2:
                    self.intersections.append((row, column))

        print(self.intersections)
        print(len(self.intersections))

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def aStarSearch(self, start, end):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        cameFrom = {}
        costSoFar = {}
        cameFrom[start] = None
        costSoFar[start] = 0
            
        while not frontier.empty():
            current = frontier.get()

            if current == end:
                break
            
            for next in self.neighbors(current):
                x, y = next
                cost = costSoFar[current] + 1
                if next not in costSoFar or cost < costSoFar[next] and self.grid[x][y] != 1:
                    costSoFar[next] = cost
                    priority = cost + self.heuristic(end, next)
                    frontier.put(next, priority)
                    cameFrom[next] = current
            
        return cameFrom, costSoFar

    def reconstructPath(self, cameFrom, start, end):
        current = end
        path = [current]
        while current != start:
            current = cameFrom[current]
            path.append(current)
        path.reverse()
        return path

    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]        
        return results

class Pacman(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image        = pygame.image.load('pacman.png')
        self.position     = position
        self.rect         = self.image.get_rect()
        self.rect.center  = self.position
        self.direction    = 0
        self.speed        = 0
        self.prevPosition = position
        self.gridLocation = (0, 0)
        self.pooledInput  = 4
        self.kU = self.kD = self.kL = self.kR = 0
        
    def update(self):
        x, y = self.position
        xVel = yVel = 0
        row, column = self.gridLocation
        
        #block collision
        blockCollisions  = pygame.sprite.spritecollide(self, game.blockS, False)
        collided = 0
        for block in blockCollisions:
            if block:
                self.speed = 0
                collided = 1

        if self.kU and game.levelCoords[row-1][column] != 1 or self.kL and game.levelCoords[row][column-1] != 1 or self.kD and game.levelCoords[row+1][column] != 1 or self.kR and game.levelCoords[row][column+1] != 1:
            if not collided: self.speed = 1
                
        #input pooling
        if self.kU:
            if game.levelCoords[row-1][column] == 1: self.pooledInput = 0
            else: self.direction = 0
        if self.kL:
            if game.levelCoords[row][column-1] == 1: self.pooledInput = 1
            else: self.direction = 1
        if self.kD:
            if game.levelCoords[row+1][column] == 1: self.pooledInput = 2
            else: self.direction = 2
        if self.kR:
            if game.levelCoords[row][column+1] == 1: self.pooledInput = 3
            else: self.direction = 3

        if self.pooledInput == 0 and game.levelCoords[row-1][column] != 1:
            self.direction   = 0
            self.pooledInput = 4
        if self.pooledInput == 1 and game.levelCoords[row][column-1] != 1:
            self.direction   = 1
            self.pooledInput = 4            
        if self.pooledInput == 2 and game.levelCoords[row+1][column] != 1:
            self.direction   = 2
            self.pooledInput = 4
        if self.pooledInput == 3 and game.levelCoords[row][column+1] != 1:
            self.direction   = 3
            self.pooledInput = 4

        #update position   
        if   self.direction == 0: yVel = -self.speed
        elif self.direction == 1: xVel = -self.speed
        elif self.direction == 2: yVel =  self.speed
        elif self.direction == 3: xVel =  self.speed
        
        nextPosition = (x + xVel, y + yVel)

        for i in range(0, len(game.levelCoords)):
            for j in range(0, len(game.levelCoords[i])):
                tmpRect = self.image.get_rect()
                tmpRect.center = nextPosition
                if self.rect.center == game.levelCoords[i][j]: self.gridLocation = (i, j)
                if tmpRect.center   == game.levelCoords[i][j]: self.gridLocation = (i, j)

        if collided:
            nextPosition = self.prevPosition
        
        self.prevPosition = self.position
        self.position     = nextPosition                
        self.rect         = self.image.get_rect()
        self.rect.center  = self.position             
                    
        #reset key presses
        self.kU = self.kD = self.kL = self.kR = 0
        
class Pellet(pygame.sprite.Sprite):

    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image       = pygame.image.load('pellet.png')
        self.position    = position
        self.rect        = self.image.get_rect()
        self.rect.center = self.position      

class Block(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image       = pygame.image.load('block.png')
        self.position    = position
        self.rect        = self.image.get_rect()
        self.rect.center = self.position

class Ghost(pygame.sprite.Sprite):
    def __init__(self, position, number):  
        pygame.sprite.Sprite.__init__(self)
        
        if number == 0: self.image = pygame.image.load('blinky.png')
        elif number == 1: self.image = pygame.image.load('inky.png')
        elif number == 2: self.image = pygame.image.load('pinky.png')
        elif number == 3: self.image = pygame.image.load('clyde.png')
            
        self.safeCorner    = (0, 0)  
        self.ghostID       = number
        self.position      = position
        self.rect          = self.image.get_rect()
        self.rect.center   = self.position
        self.gridLocation  = (0, 0)
        self.direction     = 0
        self.hitWall       = 0
        self.canMove       = 0
        self.prevDirection = 4
        self.scatter       = 0
        self.targetTile    = (0, 0)
        self.flipped       = 0
        self.path          = []
        
    def getSafeCorner(self):       
        if self.ghostID   == 0: self.safeCorner = (0, game.gridLength)
        elif self.ghostID == 1: self.safeCorner = (game.gridHeight, game.gridLength)
        elif self.ghostID == 2: self.safeCorner = (0, 0)
        elif self.ghostID == 3: self.safeCorner = (game.gridHeight, 0)

    def flipDirection(self):
        if self.direction   == 0: self.direction = 2
        elif self.direction == 1: self.direction = 3
        elif self.direction == 2: self.direction = 0
        elif self.direction == 3: self.direction = 1

    def findTargetTile(self):       
        if not self.scatter:
            self.flipped = 0
            y, x = game.pacman.gridLocation
            if self.ghostID == 0: #Blinky: Target tile is pacmans current tile
                self.targetTile = (y, x)
                
            if self.ghostID == 1: #Inky: Target tile is double the vector between blinky and pacman
                tmpX = 0
                tmpY = 0
                if game.pacman.direction == 0:
                    tmpX = x
                    tmpY = y - 2
                if game.pacman.direction == 1:
                    tmpX = x - 2
                    tmpY = y               
                if game.pacman.direction == 2:
                    tmpX = x
                    tmpY = y + 2                
                if game.pacman.direction == 3:
                    tmpX = x + 2
                    tmpY = y
                blY, blX = game.blinky.gridLocation
                self.targetTile = (blY + ((tmpY - blY) * 2), blX + ((tmpX - blX) * 2))
       
            if self.ghostID == 2: #Pinky: Target tile is 2 ahead of direction pacman is currently travelling
                if game.pacman.direction == 0: self.targetTile = (y - 2, x)
                if game.pacman.direction == 1: self.targetTile = (y, x - 2)
                if game.pacman.direction == 2: self.targetTile = (y + 2, x)
                if game.pacman.direction == 3: self.targetTile = (y, x + 2)
                    
            if self.ghostID == 3: #Clyde: If closer than 8 tiles target tile is safe corner, otherwise same as blinky
                clY, clX = self.gridLocation
                distX = x - clX
                distY = y - clY
                if distX >= 8 or distX <= -8 or distY >= 8 or distY <= -8: self.targetTile = (y, x)
                else: self.targetTile = self.safeCorner

    def update(self):
        self.hitWall = 0
        if self.targetTile == (0, 0): self.findTargetTile()
        if self.safeCorner == (0, 0): self.getSafeCorner()

        atInter = 0
        for i in game.level.intersections:
            if i == self.gridLocation:
                atInter = 1
                            
        if self.scatter and not self.flipped:
            self.flipped = 1
            self.flipDirection()
            self.targetTile = self.safeCorner

        if not self.scatter:
            self.findTargetTile()
                    
        xVel = yVel = 0
        x, y = self.position

        if not self.path:
            cameFrom, costSoFar = game.level.aStarSearch(self.gridLocation, self.targetTile)
            self.path = game.level.reconstructPath(cameFrom, self.gridLocation, self.targetTile)

        if self.canMove and not self.hitWall or atInter:
            if   self.direction == 0: yVel = -1
            elif self.direction == 1: xVel = -1
            elif self.direction == 2: yVel =  1
            elif self.direction == 3: xVel =  1

            self.position = (x + xVel, y + yVel)

        for i in range(0, len(game.levelCoords)):
            for j in range(0, len(game.levelCoords[i])):
                tmpRect = self.image.get_rect()
                tmpRect.center = (x + xVel, y + yVel)
                if self.rect.center == game.levelCoords[i][j]: self.gridLocation = (i, j)
                if tmpRect.center   == game.levelCoords[i][j]: self.gridLocation = (i, j)

        blockCollisions  = pygame.sprite.spritecollide(self, game.blockS, False)
        for block in blockCollisions:
            cameFrom, costSoFar = game.level.aStarSearch(self.gridLocation, self.targetTile)
            self.path = game.level.reconstructPath(cameFrom, self.gridLocation, self.targetTile)
            pX, pY = self.path[0]
            self.position = (25 + (pY*24), 25 + (pX*24))
            self.hitWall = 1
                
        if atInter:
            self.checkDirection()
            
        self.rect        = self.image.get_rect()
        self.rect.center = self.position

    def checkDirection(self):
        gridX, gridY = self.gridLocation
        if self.path[1]:
            pathX, pathY = self.path[1]
            if   pathX - 1 == gridX:
                self.direction = 3
                self.path.pop(0)
            elif pathX + 1 == gridX:
                self.direction = 1
                self.path.pop(0)
            elif pathY - 1 == gridY:
                self.direction = 0
                self.path.pop(0)
            elif pathY + 1 == gridY:
                self.direction = 2
                self.path.pop(0)
                
    
if __name__ == "__main__":
    game = Game()
    game.mainLoop()
