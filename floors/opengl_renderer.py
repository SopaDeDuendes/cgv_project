from OpenGL.GL import *
from person import Person
import random

# Inicializamos las personas en el piso 5
floors = [
    [],  # Piso 1
    [],  # Piso 2
    [],  # Piso 3
    [],  # Piso 4
    [Person(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) for _ in range(10)]  # Piso 5 con 10 personas
]

# Posiciones de las escaleras y zonas seguras, garantizando que no se superpongan
stair_positions = [
    (0.0, 0.6),   # Piso 1 (escalera arriba)
    (-0.6, 0.0),  # Piso 2 (escalera izquierda)
    (0.6, 0.0),   # Piso 3 (escalera derecha)
    (0.0, -0.6),  # Piso 4 (escalera abajo)
    (0.6, 0.0)    # Piso 5 (escalera derecha)
]

safe_zone_positions = [
    (-0.6, -0.6), # Piso 1
    (0.6, -0.6),  # Piso 2
    (-0.6, 0.6),  # Piso 3
    (0.6, 0.6),   # Piso 4
    (-0.6, 0.6)   # Piso 5
]

# Bandera para saber si ya hay una persona en la zona segura por piso
safe_zone_occupied = [False] * 5

def render_floor(floor_index):
    """Renderiza el piso como un cuadrado claro con paredes representando habitaciones."""
    glBegin(GL_QUADS)
    glColor3f(0.9, 0.9, 0.9)  # Color claro del piso
    glVertex2f(-0.7, -0.7)
    glVertex2f(0.7, -0.7)
    glVertex2f(0.7, 0.7)
    glVertex2f(-0.7, 0.7)
    glEnd()

    # Paredes de habitaciones
    glColor3f(0.5, 0.5, 0.5)  # Color de las paredes
    glBegin(GL_LINES)
    glVertex2f(-0.5, -0.7)
    glVertex2f(-0.5, 0.7)
    glVertex2f(0.5, -0.7)
    glVertex2f(0.5, 0.7)
    glEnd()

    # Renderizar la zona segura
    safe_x, safe_y = safe_zone_positions[floor_index]
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)  # Color verde para la zona segura
    glVertex2f(safe_x - 0.1, safe_y - 0.1)
    glVertex2f(safe_x + 0.1, safe_y - 0.1)
    glVertex2f(safe_x + 0.1, safe_y + 0.1)
    glVertex2f(safe_x - 0.1, safe_y + 0.1)
    glEnd()

    # Renderizar la escalera con líneas continuas
    stair_x, stair_y = stair_positions[floor_index]
    glBegin(GL_LINE_LOOP)
    glColor3f(0.3, 0.3, 0.3)  # Color de la escalera
    glVertex2f(stair_x - 0.1, stair_y - 0.05)
    glVertex2f(stair_x + 0.1, stair_y - 0.05)
    glVertex2f(stair_x + 0.1, stair_y + 0.05)
    glVertex2f(stair_x - 0.1, stair_y + 0.05)
    glEnd()

def render_people(floor_index):
    """Renderiza las personas y actualiza su posición en el piso actual."""
    global safe_zone_occupied

    for person in floors[floor_index]:
        # Si una persona ya está en la zona segura, no se mueve
        if person.in_safe_zone():
            continue

        # Si la zona segura aún no está ocupada, una persona va hacia ella
        if not safe_zone_occupied[floor_index]:
            person.move_towards_safe_zone(safe_zone_positions[floor_index])
            if person.in_safe_zone():
                safe_zone_occupied[floor_index] = True  # Marca que la zona segura está ocupada
        else:
            # El resto de personas se mueven hacia la escalera
            person.move_towards_stair(stair_positions[floor_index])

            # Si la persona llega a la escalera, la movemos al siguiente piso
            if person.reached_stair(stair_positions[floor_index]):
                if floor_index > 0:  # No puede bajar si está en el piso 1
                    floors[floor_index - 1].append(person)  # Mueve la persona al piso inferior
                    floors[floor_index].remove(person)  # Elimina la persona del piso actual
                    print(f'Moviendo persona del piso {floor_index + 1} al piso {floor_index}')

        # Renderizar la persona
        glColor3f(1.0, 0.0, 0.0)  # Color rojo para las personas
        glBegin(GL_QUADS)
        glVertex2f(person.x - 0.02, person.y - 0.02)
        glVertex2f(person.x + 0.02, person.y - 0.02)
        glVertex2f(person.x + 0.02, person.y + 0.02)
        glVertex2f(person.x - 0.02, person.y + 0.02)
        glEnd()

    print(f"Hay {len(floors[floor_index])} personas en el piso {floor_index + 1}")

def render_floor_with_people(floor_index):
    """Renderiza el piso y las personas moviéndose en él."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    render_floor(floor_index)
    render_people(floor_index)
    glFlush()
