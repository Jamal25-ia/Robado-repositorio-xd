"""
    3D Game
"""
################ Imports ######################################################
import pygame
import math
################ Configuration ################################################
pygame.init()

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,255)
WHITE = (255,255,255)

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 500
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 300
MODEL_SURFACE = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
MODEL_RECT = pygame.Rect(10,50,WINDOW_WIDTH,WINDOW_HEIGHT)

VIEW_SURFACE = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
VIEW_RECT = pygame.Rect(330,50,WINDOW_WIDTH,WINDOW_HEIGHT)

PROJECTION_SURFACE = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
PROJECTION_RECT = pygame.Rect(650,50,WINDOW_WIDTH,WINDOW_HEIGHT)

font_name = pygame.font.match_font('arial')
################ Helper Functions #############################################

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def round(point):
    return (int(point[0]),int(point[1]))

def translate(point,translation):
    (x,y) = point
    (dx,dy) = translation
    return (x + dx,y + dy)

def rotate_point(point,angle):
    (x,y) = point
    theta = math.radians(angle)
    rotated_x = x*math.cos(theta) + y*math.sin(theta)
    rotated_y = -x*math.sin(theta) + y*math.cos(theta)
    return (rotated_x,rotated_y)

def scale(point,factor_x,factor_y=None):
    if factor_y==None:
        factor_y = factor_x
    (x,y) = point
    return (x*factor_x,y*factor_y)

################ Classes ######################################################

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 16
        self.position = (150,150)
        self.direction = 0
        self.speed = 2
        self.camera_z = 30

        self.original_image = pygame.Surface((32,32))
        pygame.draw.circle(self.original_image,RED,(16,16),self.radius)
        pygame.draw.line(self.original_image,BLACK,(16,16),(32,16))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()

    def update(self):
        #take inputs
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.direction += 2
            if self.direction > 360:
                self.direction -= 360

        if keystate[pygame.K_RIGHT]:
            self.direction -= 2
            if self.direction < 0:
                self.direction += 360

        if keystate[pygame.K_UP]:
            dx =  self.speed*math.cos(math.radians(self.direction))
            dy = -self.speed*math.sin(math.radians(self.direction))
            change_in_position = (dx,dy)
            self.position = translate(self.position,change_in_position)

        if keystate[pygame.K_DOWN]:
            dx = -self.speed*math.cos(math.radians(self.direction))
            dy =  self.speed*math.sin(math.radians(self.direction))
            change_in_position = (dx,dy)
            self.position = translate(self.position,change_in_position)

        self.model_to_world_transform()
        self.world_to_view_transform()

    def model_to_world_transform(self):
        #apply model to world coordinate transformation
        #rotate first
        self.image = pygame.transform.rotate(self.original_image, self.direction)

        #then translate into place
        self.rect = self.image.get_rect()
        self.rect.center = round(self.position)

    def world_to_view_transform(self):
        #apply world to view coordinate transformation
        #rotate then transate
        rotated_image = pygame.transform.rotate(self.original_image, 90)
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = (WINDOW_WIDTH//2,WINDOW_HEIGHT//2)
        #blit to view
        VIEW_SURFACE.blit(rotated_image,rotated_rect)

class Wall(pygame.sprite.Sprite):
    def __init__(self,pos_a,pos_b,colour):
        pygame.sprite.Sprite.__init__(self)
        self.pos_a = pos_a
        self.pos_b = pos_b
        self.colour = colour
        self.z = 0
        self.height = 80

        width = max(abs(pos_a[0] - pos_b[0]),1)
        height = max(abs(pos_a[1] - pos_b[1]),1)
        left = min(pos_a[0],pos_b[0])
        top = min(pos_a[1],pos_b[1])
        self.image = pygame.Surface((width,height))

        pygame.draw.line(self.image,self.colour,(self.pos_a[0]-left,self.pos_a[1]-top),\
            (self.pos_b[0]-left,self.pos_b[1]-top))
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top

    def update(self):
        #wall is already defined in world coordinates
        self.world_to_view_transform()
        self.view_to_projection_transform()

    def world_to_view_transform(self):
        #find position relative to camera
        cam = (-player.position[0],-player.position[1])
        self.pos_a_view = translate(self.pos_a,cam)
        self.pos_b_view = translate(self.pos_b,cam)
        #rotate 90 degrees counter clockwise, then opposite camera motion
        opposite_cam = 90-player.direction
        self.pos_a_view = rotate_point(self.pos_a_view,opposite_cam)
        self.pos_b_view = rotate_point(self.pos_b_view,opposite_cam)
        pygame.draw.line(VIEW_SURFACE,self.colour,
                            round(translate(self.pos_a_view,(WINDOW_WIDTH//2,WINDOW_HEIGHT//2))),
                            round(translate(self.pos_b_view,(WINDOW_WIDTH//2,WINDOW_HEIGHT//2))))

    def view_to_projection_transform(self):
        #Projection transformation
        #in the view portal, a point's height (y-coordinate) can represent its depth
        depth_a = max(abs(self.pos_a_view[1]),0.01)
        x_a = self.pos_a_view[0]/depth_a
        top_a = -(self.z+self.height-player.camera_z)/depth_a
        bottom_a = -(self.z-player.camera_z)/depth_a

        depth_b = max(abs(self.pos_b_view[1]),0.01)
        x_b = self.pos_b_view[0]/depth_b
        top_b = -(self.z+self.height-player.camera_z)/depth_b
        bottom_b = -(self.z-player.camera_z)/depth_b

        points = [
                    (x_a,top_a),
                    (x_b,top_b),
                    (x_b,bottom_b),
                    (x_a,bottom_a)
                ]
        """
            These points are now in normalised device coordinates (NDC),
            They range from -1 to 1 where:
                x: -1 is left, 0 is centre, 1 is right
                y: -1 is top, 0 is centre, 1 is bottom
            and values outside this range are off the screen.

            In order to graph these points we need to multiply them by half the screen width and half the screen height,
            then add the position of the screen centre
        """

        for i in range(len(points)):
            points[i] = scale(points[i],WINDOW_WIDTH//2,WINDOW_HEIGHT//2)
            points[i] = round(translate(points[i],(WINDOW_WIDTH//2,WINDOW_HEIGHT//2)))

        pygame.draw.polygon(PROJECTION_SURFACE, self.colour, points,1)

################ Game Objects #################################################
player = Player()
GAME_OBJECTS = pygame.sprite.Group()
RESTRICTED = pygame.sprite.Group()
GAME_OBJECTS.add(player)

wall = Wall((10,10),(290,10),GREEN)
GAME_OBJECTS.add(wall)
RESTRICTED.add(wall)
wall = Wall((290,10),(290,290),BLUE)
GAME_OBJECTS.add(wall)
RESTRICTED.add(wall)
wall = Wall((290,290),(10,290),YELLOW)
GAME_OBJECTS.add(wall)
RESTRICTED.add(wall)
wall = Wall((10,290),(10,10),PURPLE)
GAME_OBJECTS.add(wall)
RESTRICTED.add(wall)
################ Game Loop ####################################################
running = True
while running:
    ################ Reset Surfaces ###########################################
    VIEW_SURFACE.fill(BLACK)
    MODEL_SURFACE.fill(BLACK)
    PROJECTION_SURFACE.fill(BLACK)
    SCREEN.fill(BLACK)
    ################ Handle Events ############################################
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False
    ################ Update ###################################################
    GAME_OBJECTS.update()
    ################ Render ###################################################
    GAME_OBJECTS.draw(MODEL_SURFACE)

    SCREEN.blit(MODEL_SURFACE,MODEL_RECT)
    SCREEN.blit(VIEW_SURFACE,VIEW_RECT)
    SCREEN.blit(PROJECTION_SURFACE,PROJECTION_RECT)

    pygame.draw.rect(SCREEN,WHITE,MODEL_RECT,1)
    draw_text(SCREEN,"World Coordinates",16,70,20)
    pygame.draw.rect(SCREEN,WHITE,VIEW_RECT,1)
    draw_text(SCREEN,"View Coordinates",16,390,20)
    pygame.draw.rect(SCREEN,WHITE,PROJECTION_RECT,1)
    draw_text(SCREEN,"Projection Coordinates",16,730,20)
    ################ Clock etc ################################################
    CLOCK.tick(60)
    fps = CLOCK.get_fps()
    pygame.display.set_caption("Running at "+str(int(fps))+" fps")
    pygame.display.update()

################ Shutdown #####################################################
pygame.quit()