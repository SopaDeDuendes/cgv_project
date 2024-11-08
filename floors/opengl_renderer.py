from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from person import Person
import random
import math

# Posiciones de personas, escaleras y zonas seguras
floors = [
    [], [], [], [], 
    [Person(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) for _ in range(10)]
]

# Cambiamos las posiciones de escaleras y zonas seguras a (x, z)
stair_positions = [
    (0.0, 0.6), (-0.6, 0.0), (0.6, 0.0), (0.0, -0.6), (0.6, 0.0)
]

safe_zone_positions = [
    (-0.6, -0.6), (0.6, -0.6), (-0.6, 0.6), (0.6, 0.6), (-0.6, 0.6)
]


safe_zone_occupied = [False] * 5

# Variables de cámara
camera_angle_x = 0
camera_angle_y = 20  # Ajustar este valor para cambiar la vista vertical
camera_distance = 5   # Aumentar la distancia para ver todo el edificio
last_mouse_x = 0
last_mouse_y = 0
last_time = 0  # Tiempo de la última actualización

def init_3d_view():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def set_camera():
    glLoadIdentity()
    
    # Posición de la cámara usando ángulos y distancia
    camera_x = camera_distance * math.sin(math.radians(camera_angle_x)) * math.cos(math.radians(camera_angle_y))
    camera_z = camera_distance * math.sin(math.radians(camera_angle_y))  # Cambia `y` a `z`
    camera_y = camera_distance * math.cos(math.radians(camera_angle_x)) * math.cos(math.radians(camera_angle_y))

    # Establece la vista de la cámara
    gluLookAt(
        camera_x,
        camera_y,
        camera_z,
        0, 0, 0,   
        0, 1, 0   
    )


def draw_cube(x, y, z, size, color):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidCube(size)
    glPopMatrix()

def render_floor_3d(floor_index, height):
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(-0.7, height, -0.7)
    glVertex3f(0.7, height, -0.7)
    glVertex3f(0.7, height, 0.7)
    glVertex3f(-0.7, height, 0.7)
    glEnd()
    
    # Renderiza las paredes
    glColor3f(0.5, 0.5, 0.5)
    wall_height = 0.1
    draw_cube(-0.5, height + wall_height / 2, 0, 0.02, (0.5, 0.5, 0.5))
    draw_cube(0.5, height + wall_height / 2, 0, 0.02, (0.5, 0.5, 0.5))
    draw_cube(0, height + wall_height / 2, 0.5, 0.02, (0.5, 0.5, 0.5))
    draw_cube(0, height + wall_height / 2, -0.5, 0.02, (0.5, 0.5, 0.5))
    
    # Zonas seguras y escaleras
    safe_x, safe_z = safe_zone_positions[floor_index]
    draw_cube(safe_x, height + 0.02, safe_z, 0.1, (0.0, 1.0, 0.0))
    stair_x, stair_z = stair_positions[floor_index]
    draw_cube(stair_x, height + 0.02, stair_z, 0.1, (0.3, 0.3, 0.3))


def render_people_3d(floor_index, height, delta_time):
    move_speed = 0.05  # velocidad de moviemiento
    people_on_floor = floors[floor_index]

    # Verificar si alguien ya está en la zona segura
    safe_zone_occupied = False
    for person in people_on_floor:
        if person.in_safe_zone():
            safe_zone_occupied = True
            break  # Si encontramos a alguien en la zona segura, no seguimos buscando

    for person in people_on_floor:
        if person.in_safe_zone():
            continue  # Si la persona ya está en la zona segura, no hacer nada

        # Mueve la persona hacia la zona segura solo si no está ocupada
        person.move_towards_safe_zone(safe_zone_positions[floor_index], move_speed * delta_time, safe_zone_occupied)

        if person.in_safe_zone():
            safe_zone_occupied = True  # Marca la zona segura como ocupada

        # Si la zona segura está ocupada, mueve la persona hacia las escaleras
        if safe_zone_occupied:
            person.move_towards_stair(stair_positions[floor_index], move_speed * delta_time)
            if person.reached_stair(stair_positions[floor_index]) and floor_index > 0:
                floors[floor_index - 1].append(person)  # Mueve la persona al otro piso
                floors[floor_index].remove(person)

        # Dibuja la persona en el piso
        draw_cube(person.x, height + 0.05, person.y, 0.04, (1.0, 0.0, 0.0))


def render_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    set_camera()
    
    global last_time
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0  # Tiempo en segundos
    delta_time = current_time - last_time  
    last_time = current_time

    for i, _ in enumerate(floors):
        height = i * 0.3  # Espaciado entre los pisos
        render_floor_3d(i, height)
        render_people_3d(i, height, delta_time)  
    
    glFlush()   
    glutSwapBuffers()

def animate(value):
    render_scene()
    glutTimerFunc(50, animate, 0)  

def init():
    glEnable(GL_DEPTH_TEST)
    init_3d_view()

# Mover cámara con mouse
def mouse_motion(x, y):
    global camera_angle_x, camera_angle_y, last_mouse_x, last_mouse_y
    dx = x - last_mouse_x
    dy = y - last_mouse_y
    camera_angle_x += dx * 0.2
    camera_angle_y -= dy * 0.2
    camera_angle_y = max(-89, min(89, camera_angle_y))  # Limitar el ángulo vertical
    last_mouse_x = x
    last_mouse_y = y
    glutPostRedisplay()

def mouse_wheel(button, direction, x, y):
    global camera_distance
    if direction > 0:
        camera_distance -= 0.1
    else:
        camera_distance += 0.1
    camera_distance = max(1.0, min(10.0, camera_distance))
    glutPostRedisplay()

def mouse(button, state, x, y):
    global last_mouse_x, last_mouse_y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        last_mouse_x = x
        last_mouse_y = y

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"3D Escape Simulation")
init()
glutDisplayFunc(render_scene)
glutMotionFunc(mouse_motion)
glutMouseFunc(mouse)
glutMouseWheelFunc(mouse_wheel)

# Iniciar animación
animate(0)  
glutMainLoop()
