import pyglet
from pyglet.window import key

import random
from tom_lib.vectors import Vec2, Vec, Angle
from math import sin, cos, atan, pi, tau, sqrt

# Controls:
#   Move:                   a, w, s, d
#   Create new random maze: space
#   Toggle 3D view:         3
#   Toggle fullscreen:      f
#   Hide cursor:            C

# notes:
#   finish is a wall portal to the next level
#   improve collision formula
#   improve coordinate system
#   start in the middle of the triangle
#   give it a random angle too?
#   evil labyrinth, poner el final en la ultima pared o habitacion que miras
#     (también se puede implementar en el viejo laberinto)
#   allow loops to mirror image (it doesn't do that yet, right?)
#   consider more polygon types (square, pentagon, etc, could help structure the labyrinth better)
#   agregar colores en el suelo o algo para referencia visual
#   fix doors formula to fit ratio (kinda complex)
#   fix black triangles bug
#   fix weird walls when barely covered
#   labyrinth is extended after you reach certain spots (like it is 1 length, then 2, then n.)
#      loops can be created this way too
#      can speedrun this
#   green triangle room is finish?
#   implement 3D view, this should be very easy
#   eventually make 3D puzzles
#   hacer un loop de punteros hasta llegar al puntero que apunte a si mismo (i.e. pointer[x] = x)


# - try choosing connections instead of loops, that should make multiple 3 door rooms more rare
# - crear variable seen_walls
# - infinite maze, parameter indicates how far the exit is, you can get lost inside of it, beware.
#   - set a number c: 2 < c < 3, create rooms with connections trying to keep the average number of connections close to that
# - be careful with passing two walls or wall hits before passing and that stuff
# - poner puntos en vertices sin paredes
# - falta cambiar de habitacion al moverse
# - cortar las lineas al pasarse de largo
#   - quizas ir acontando los angulos cada vez que pasas por un par de puntos?
# - IMPLEMENT LOOPS!!!!!!!!!
# - some kind of mutable labyrinth
# * MOVING TRIANGLES!!
# - small blind spot behind flying dots
# - void walls (walls out of range)


config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True, depth_size=24)
window = pyglet.window.Window(resizable=True, fullscreen=True, config=config)

# pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
# pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)


width = 1366
height = 768

min_side_size = 100
max_side_size = int(min_side_size*1.9)


random.seed(9)

infinite = False
ratio = 2.2

# experiment with low values, they create very interesting patterns.
n = 4
loops = 2



wall_size = 2
char_size = 6
speed = 4


# max_transformation_speed = 0.01
print_grey_lines = True

_3D_perspective = False

mouse_movements = [[0 for i in range(3)] for j in range(2)]
mouse_speed = 1

if not _3D_perspective:
    exclusive_mouse = False
    max_room_iterations = 15
    # max_total_lines = 200
else:
    window.set_exclusive_mouse(True)
    exclusive_mouse = True
    max_room_iterations = 25
    # max_total_lines = 200

created_rooms = n
doors = 0

# 3D perspective
rotation_speed = 1
vertical_ratio = 1.5
horizontal_ratio = 1.5
wall_height = 40
character_height = 40
thick_walls = False

character_angle = 0



rooms_directions = [[False, False, False] for i in range(n)]
triangles_sides_size = [[random.randint(min_side_size, max_side_size) for j in range(3)] for i in range(n)]
triangles_sides_size_properties = [[[random.random(), random.random()] for j in range(3)] for i in range(n)]


# def get_side_size(room, direction):
#     c0, c1 = triangles_sides_size_properties[room][direction]
#     x = c0 * pi + c1 * t * max_transformation_speed
#     return (cos(x)+1)/2 * (max_side_size - min_side_size) + min_side_size

def average(l):
    return sum(l)/len(l)

def get_triangle_vertex(v1, v2, room, direction):
    l = triangles_sides_size[room][direction]
    r1 = triangles_sides_size[room][(direction + 1) % 3]
    r2 = triangles_sides_size[room][(direction + 2) % 3]
    # l =  get_side_size(room, direction)
    # r1 = get_side_size(room, (direction + 1) % 3)
    # r2 = get_side_size(room, (direction + 2) % 3)

    d = (r1**2 - r2**2) / (2*l) + l / 2
    h = sqrt(r1 ** 2 - d ** 2)
    vn1 = (v2-v1) / l
    vn2 = Vec2(vn1.y, -vn1.x)
    return v1 + d * vn1 + h * vn2

def create_labyrinth():
    global rooms_directions, triangles_sides_size, triangles_sides_size_properties
    group_indexes = [i for i in range(n)]
    # group_indexes = [[i] for i in range(n)]
    group_rooms = [[i] for i in range(n)]
    available_rooms = [i for i in range(n)]
    random.shuffle(available_rooms)
    available_directions = [[0, 1, 2] for i in range(n)]

    rooms_directions = [[False, False, False] for i in range(n)]
    triangles_sides_size = [[random.randint(min_side_size, max_side_size) for j in range(3)] for i in range(n)]
    triangles_sides_size_properties = [[[random.random(), random.random()] for j in range(3)] for i in range(n)]

    available_doors = [(r, d) for d in range(3) for r in range(n)] # ---
    random.shuffle(available_doors)

    for i in range(n-1+loops):

        # creating with rooms instead of doors:
        # ---
        a = random.choice(available_rooms)


        for b in available_rooms:
            if group_indexes[a] != group_indexes[b] or i >= (n-1):
                break
        else:
            print("error formando el laberinto")
            break
        # ---

        a_d = random.choice(available_directions[a])
        b_d = random.choice(available_directions[b])

        # a, a_d = available_doors[0]
        # available_doors.pop(0)
        # for j in range(len(available_doors)):
        #     if group_indexes[a] != group_indexes[available_doors[j][0]] or i >= (n - 1):
        #     # if group_indexes[a][0] != group_indexes[available_doors[j][0]][0] or i >= (n - 1):
        #         b, b_d = available_doors[j]
        #         # b, b_d = available_doors[j][0]
        #         available_doors.pop(j)
        #         break
        # else:
        #     print("fail")


        not_partially_seen_walls.discard((a, a_d))
        not_partially_seen_walls.discard((b, b_d))
        not_totally_seen_walls.discard((a, a_d))
        not_totally_seen_walls.discard((b, b_d))

        available_directions[a].remove(a_d)
        if a != b or a_d != b_d:
            available_directions[b].remove(b_d)

        if len(available_directions[a]) == 0:
            available_rooms.remove(a)
        if len(available_directions[b]) == 0 and a != b:
            available_rooms.remove(b)

        # rooms_directions[a][a_d] = b
        # rooms_directions[b][b_d] = a
        rooms_directions[a][a_d] = (b, b_d)
        rooms_directions[b][b_d] = (a, a_d)

        s = random.randint(min_side_size, max_side_size)
        r1 = random.random()
        r2 = random.random()
        triangles_sides_size[a][a_d] = s
        triangles_sides_size[b][b_d] = s
        triangles_sides_size_properties[a][a_d] = [r1, r2]
        triangles_sides_size_properties[b][b_d] = [r1, r2]

        if i < n - 1:
            group_rooms[group_indexes[a]] += group_rooms[group_indexes[b]]
            # group_indexes[group_indexes[b]][0] = group_indexes[group_indexes[a]][0]

            for e in group_rooms[group_indexes[b]]:
                group_indexes[e] = group_indexes[a]

def create_room(room, direction):
    global created_rooms, doors

    rooms_directions[room][direction] = (created_rooms, 0)
    rooms_directions.append([(room, direction), False, False])
    triangles_sides_size.append([triangles_sides_size[room][direction],
                                 random.randint(min_side_size, max_side_size),
                                 random.randint(min_side_size, max_side_size)])
    directions = [1, 2]
    random.shuffle(directions)

    created_rooms += 1
    doors += 1
    # print(doors / created_rooms)
    for i in range(2):
        # if (doors) / created_rooms < ratio + 2 * random.random() * (ratio - 2) - (ratio - 2):
        # if (doors + 0.5) / created_rooms < ratio + random.random()*2 - 1:
        # if ratio > doors / (created_rooms):
        #     print(created_rooms, doors)
        rnd = random.random()
        # print(room, created_rooms, round(doors / created_rooms, 3), - ratio * created_rooms + doors)
        # if (doors) / created_rooms < 2 + 2 * r * (ratio - 2):
        if doors / created_rooms < ratio or rnd < (ratio - 1) / 2:
            rooms_directions[created_rooms-1][directions[i]] = None
            doors += 1

def create_infinite_labyrinth():

    # add creation of room in room 0

    global created_rooms, doors, rooms_directions, triangles_sides_size, triangles_sides_size_properties
    # rooms_directions = [[False, False, False] for i in range(n)]
    created_rooms = n
    doors = 0

    rooms_directions = [[False, False, False] for i in range(n)]
    triangles_sides_size = [[random.randint(min_side_size, max_side_size) for j in range(3)] for i in range(n)]
    triangles_sides_size_properties = [[[random.random(), random.random()] for j in range(3)] for i in range(n)]


    d1 = random.randint(0, 2)
    d2 = random.randint(0, 2)

    rooms_directions[0][d2] = None

    for i in range(n-1):
        directions = [0, 1, 2]
        random.shuffle(directions)
        directions.remove(d2)
        d1 = directions[0]
        d2 = directions[1]
        directions.remove(d1)
        rooms_directions[i][d1] = (i + 1, d2)
        rooms_directions[i+1][d2] = (i, d1)

        doors += 2
        s = random.randint(min_side_size, max_side_size)
        triangles_sides_size[i][d1] = s
        triangles_sides_size[i+1][d2] = s
        # d1 = d2
        # if doors / (i + 1) < ratio:# + random.random() * 2 - 1:
        # if doors / (i + 1) < 2 + 2 * random.random() * (ratio - 2):
        if doors / (i + 1) < ratio or random.random() < (ratio - 1) / 2:
        # if ratio > doors / (i + 1):
            rooms_directions[i][directions[0]] = None
            doors += 1
    directions = [0, 1, 2]
    random.shuffle(directions)
    directions.remove(d2)

    doors += 1

    for i in range(2):
        # if (doors) / created_rooms < ratio:# + random.random() * 2 - 1:
        # if (doors) / created_rooms < 2 + 2 * random.random() * (ratio - 2):
        # if ratio > doors / (n):
        if doors / (i + 1) < ratio or random.random() < (ratio - 1) / 2:
            rooms_directions[n-1][directions[i]] = None
            doors += 1
            # create_room(i, available_directions[0])
        # agregar puertas a la ultima habitacion
        # print(rooms_directions)

t = 0
current_room = 0
# room_angle = 0
# pos = Vec2(-5,20)
# visited_rooms = {i for i in range(1, n)}
# room_v0 = Vec2(15, -40)
# room_v1 = room_v0 + triangles_sides_size[current_room][0]*Vec2(0,1)
# room_v2 = get_triangle_vertex(room_v1, room_v0, current_room, 0)
room_vexs = [Vec2(10,10), Vec2(10,10), Vec2(10,10)]  # [room_v0, room_v1, room_v2]
max_lines = 0
not_totally_seen_walls = {(r, i) for r in range(n) for i in range(3)}
not_partially_seen_walls = {(r, i) for r in range(n) for i in range(3)}
def start():
    global current_room, visited_rooms, room_vexs, max_lines, not_partially_seen_walls, not_totally_seen_walls

    ratio = 2.3
    created_rooms = n
    doors = 0

    if infinite:
        create_infinite_labyrinth()
    else:
        create_labyrinth()

    current_room = 0
    visited_rooms = {i for i in range(1, n)}
    room_v0 = Vec2(15, -40)
    room_v1 = room_v0 + triangles_sides_size[current_room][0]*Vec2(0,1)
    room_v2 = get_triangle_vertex(room_v1, room_v0, current_room, 0)
    room_vexs = [room_v0, room_v1, room_v2]
    max_lines = 0
    not_totally_seen_walls = {(r, i) for r in range(n) for i in range(3)}
    not_partially_seen_walls = {(r, i) for r in range(n) for i in range(3)}

start()

keys_pressed = {
}
keys_just_pressed = {
}


@window.event
def on_resize(new_width, new_height):
    global width, height
    width = new_width
    height = new_height


@window.event
def on_key_press(symbol, modifiers):
    keys_pressed[symbol] = True
    keys_just_pressed[symbol] = True


@window.event
def on_key_release(symbol, modifiers):
    keys_pressed.pop(symbol, None)
    keys_just_pressed.pop(symbol, None)

walls = []
void_walls = []
grey_lines = []
total_lines = 0
flying_vertexes = set()


def move(v):
    global pos, current_room, room_vexs, visited_rooms

    print("room_vexs", room_vexs)

    v *= speed
    new_room_vexs = [r-v for r in room_vexs]
    new_current_room = current_room
    if min([abs(i) for i in new_room_vexs]) < char_size/2:
        return

    # for i in range(3):
    i = 0
    # print(len(not_partially_seen_walls), len(not_totally_seen_walls))
    while i < 3:
        print("in while", i)
        # dist = ((new_room_vexs[(i+1)%3] - new_room_vexs[i]) * Vec(0, 0, 1)).normalized().dot(new_room_vexs[i])
        dist = (new_room_vexs[(i + 1) % 3] - new_room_vexs[i]) \
            .rotated_270() \
            .normalized() \
            .dot(new_room_vexs[i])

        if dist < char_size/2:
            # print(f"side {i}", rooms_directions[current_room][i])
            if not rooms_directions[new_current_room][i]:
                # break
                print("in while return")
                return
            if dist < 0:
                print("dist < 0")
                # print(current_room, created_rooms, round(doors / created_rooms, 3), - ratio * created_rooms + doors)
                # print("yes", i)
                new_current_room, incoming_direction = rooms_directions[new_current_room][i]
                # print("room:", new_current_room, created_rooms, doors, doors / created_rooms)
                new_vex = get_triangle_vertex(new_room_vexs[i], new_room_vexs[(i+1)%3], new_current_room, incoming_direction)
                new_room_vexs[(0+incoming_direction)], new_room_vexs[(1+incoming_direction)%3], new_room_vexs[(2+incoming_direction)%3] = new_room_vexs[(i+1) % 3], new_room_vexs[i], new_vex
                visited_rooms.discard(current_room)
                i = 0
                continue

                # room_vexs = new_room_vexs
                # print(len(visited_rooms))
            # else:
            #     print("no", i)
            #     # i = 0
        i += 1
    current_room = new_current_room
    room_vexs = new_room_vexs

@window.event
def on_mouse_motion(x, y, dx, dy):
    global character_angle
    if _3D_perspective:
        character_angle -= dx/300 * rotation_speed
    else:
        return
        mouse_movements[0][t % len(mouse_movements[0])] = dx
        mouse_movements[1][t % len(mouse_movements[1])] = dy


def f(dt):
    global t, max_lines, keys_just_pressed, walls, void_walls, total_lines, flying_vertexes, grey_lines, \
        character_angle, exclusive_mouse, _3D_perspective

    if key.F in keys_just_pressed:
        window.set_fullscreen(not window.fullscreen)
        if not window.fullscreen:
            window.set_exclusive_mouse(False)
            exclusive_mouse = False
            # window.set_mouse_visible(True)
        else:
            window.set_exclusive_mouse(True)
            exclusive_mouse = True
            # window.set_mouse_visible(False)
    if key._3 in keys_just_pressed:
        _3D_perspective = not _3D_perspective

    if key.SPACE in keys_just_pressed:
        start()

    if key.C in keys_just_pressed:
        exclusive_mouse = not exclusive_mouse
        window.set_exclusive_mouse(exclusive_mouse)

    if not _3D_perspective:

        direction = Vec2(average(mouse_movements[0]), average(mouse_movements[1])) * mouse_speed
        if direction:
            move(direction)
        direction = Vec2(0, 0)

        mouse_movements[0][(t+1) % len(mouse_movements[0])] = 0
        mouse_movements[1][(t+1) % len(mouse_movements[1])] = 0

        if key.UP in keys_pressed or key.W in keys_pressed:
            direction += Vec2(0, 1)
            # move(Vec2(0, 1))
        if key.DOWN in keys_pressed or key.S in keys_pressed:
            direction += Vec2(0, -1)
            # move(Vec2(0, -1))
        if key.RIGHT in keys_pressed or key.D in keys_pressed:
            direction += Vec2(1, 0)
            # move(Vec2(1, 0))
        if key.LEFT in keys_pressed or key.A in keys_pressed:
            direction += Vec2(-1, 0)
            # move(Vec2(-1, 0))
        if direction:
            move(direction.normalized()*dt*60)
    else:
        angle = character_angle
        direction = Vec2(0, 0)
        if key.D in keys_pressed:
            direction += Vec2(cos(angle-pi/2), sin(angle-pi/2))
            # move(Vec2(cos(angle-pi/2), sin(angle-pi/2)))
        if key.A in keys_pressed:
            direction += Vec2(cos(angle+pi/2), sin(angle+pi/2))
            # move(Vec2(cos(angle+pi/2), sin(angle+pi/2)))
        if key.W in keys_pressed:
            direction += Vec2(cos(angle), sin(angle))
            # move(Vec2(cos(angle), sin(angle)))
        if key.S in keys_pressed:
            direction += Vec2(-cos(angle), -sin(angle))
            # move(Vec2(-cos(angle), -sin(angle)))
        if direction:
            move(direction.normalized()*dt*60)
    keys_just_pressed = {}


    # holes = [(0, tau)]
    walls = []
    void_walls = []
    grey_lines = []
    total_lines = 0
    flying_vertexes = {v for v in room_vexs}

    def create_wall(v1, v2, a1, a2):
        global total_lines
        total_lines += 1

        a = (v2-v1).angle() - Angle(pi/2)
        a1 = max(v1.angle(), a1)
        a2 = min(v2.angle(), a2)
        h = Vec2(cos(a), sin(a)).dot(v1)
        d1 = h / cos(a1-a)
        d2 = h / cos(a2-a)
        return (d1 * Vec2(cos(a1), sin(a1)),
                d2 * Vec2(cos(a2), sin(a2)))

    def explore_room(i, room, incoming_direction, v1, v2, a1, a2):

        # if total_lines > max_total_lines:
        #     return

        if i >= max_room_iterations:
            void_walls.append((abs(v1) * Vec2(cos(a1), sin(a1)), abs(v2) * Vec2(cos(a2), sin(a2))))
            return
        if print_grey_lines:
            grey_lines.append(create_wall(v1, v2, a1, a2))
        v3 = get_triangle_vertex(v1, v2, room, incoming_direction)
        a3 = a4 = min(max(v3.angle(), a1), a2)

        if a1 != a3 and a3 != a2:
            flying_vertexes.add(v3)

        # if a3 != a1:
        if a3 > a1:
            d = (incoming_direction+1) % 3
            if a3 == a2 and a2 == v2.angle() and thick_walls and not _3D_perspective:
                # print("yes")
                # print("yes")
                a4 = a3 - Angle(atan(wall_size / 2 / abs(v2)))
                void_walls.append((abs(v2)*Vec2(cos(a4), sin(a4)), v2))
                # print(abs(v3))

            if rooms_directions[room][d] is None:
                create_room(room, d)

            if rooms_directions[room][d]:
                explore_room(i + 1, *rooms_directions[room][d], v1, v3, a1, a4)

            else:
                not_partially_seen_walls.discard((room, d))
                if a1 == v1.angle() and a3 == v3.angle():
                    flying_vertexes.discard(v1)
                    flying_vertexes.discard(v3)
                    not_totally_seen_walls.discard((room, d))
                    walls.append((v1, v3))
                else:
                    walls.append(create_wall(v1, v3, a1, a4))
                    flying_vertexes.discard(v1)
                    flying_vertexes.discard(v3)

        # if a3 != a2:
        if a3 < a2:
            d = (incoming_direction + 2) % 3
            # print(a3, a1, v1.angle(), a3 == a1, a1 == v1.angle())
            if a3 == a1 and a1 == v1.angle() and thick_walls and not _3D_perspective:
                a4 = a3 + Angle(atan(wall_size / 2 / abs(v1)))
                void_walls.append((v1, abs(v1) * Vec2(cos(a4), sin(a4))))

            if rooms_directions[room][d] is None:
                create_room(room, d)

            if rooms_directions[room][d]:
                explore_room(i+1, *rooms_directions[room][d], v3, v2, a4, a2)

            else:
                not_partially_seen_walls.discard((room, d))
                if a3 == v3.angle() and a2 == v2.angle():
                    flying_vertexes.discard(v3)
                    flying_vertexes.discard(v2)
                    not_totally_seen_walls.discard((room, d))
                    walls.append((v3, v2))
                else:
                    walls.append(create_wall(v3, v2, a4, a2))
                    flying_vertexes.discard(v2)
                    flying_vertexes.discard(v3)


    for i in range(3):

        v1 = room_vexs[i]
        v2 = room_vexs[(i+1) % 3]
        a1 = v1.angle()
        a2 = v2.angle()
        # if len(keys_pressed) > 0:
        #     print("i:", i)

        if rooms_directions[current_room][i] is None:
            create_room(current_room, i)

        elif not rooms_directions[current_room][i]:

            not_totally_seen_walls.discard((current_room, i))
            not_partially_seen_walls.discard((current_room, i))
            walls.append((v1, v2))
            flying_vertexes.discard(v1)
            flying_vertexes.discard(v2)
            # not_partially_seen_walls.discard()
            continue
        explore_room(0, *rooms_directions[current_room][i], v1, v2, a1, a2)

    max_lines = max(max_lines, total_lines)
    # print("max_lines:", max_lines)
    t += 1


@window.event
def on_draw():
    window.clear()
    # global horizontal_ratio
    # vec = Vec2(width/2, height/2)
    # if print_grey_lines:
    #     stroke(127)
    #     for l in grey_lines:
    #         l[0].y *= -1
    #         l[1].y *= -1
    #         line(*l[0]+vec, *l[1]+vec)
    #
    # stroke(255)
    # strokeWeight(3)
    triangles = []
    lines = []
    dots = []
    # cambiar esto por centro de la ventana (teniendo en cuenta el tamaño)
    h_offset = width/2
    v_offset = height/2



    if _3D_perspective:
        # vertical_ratio = 1
        # horizontal_ratio = 1
        # wall_height = 100
        # character_height = 200
        # a

        # proyective_plane_distance = max(h_offset, v_offset) / min()

        v1 = Vec2(cos(character_angle), sin(character_angle))
        v2 = Vec2(cos(character_angle - pi/2), sin(character_angle - pi/2))

        # h = horizontal_ratio
        # print("h", horizontal_ratio)
        # h = horizontal_ratio
        horizontal_ratio = width / 3  # no 45°
        vertical_ratio = horizontal_ratio  # height / 2

        vertices = []
        for w in walls:
            p1 = w[0]
            p2 = w[1]
            p1_vz = p1.dot(v1)
            p2_vz = p2.dot(v1)
            p1_vx = p1.dot(v2)
            p2_vx = p2.dot(v2)

            if p1_vz <= 0 and p2_vz <= 0:
                continue

            if p1_vz <= 0:
                i = -(p1_vz-0.0001) / (p2_vz - p1_vz)
                # print(1, p1_vz, p2_vz, i)
                p1_vz = i * p2_vz + (1-i) * p1_vz
                p1_vx = i * p2_vx + (1 - i) * p1_vx

            if p2_vz <= 0:
                i = -(p2_vz-0.0001) / (p1_vz - p2_vz)
                # print(2, p2_vz, p1_vz, i)
                p2_vz = i * p1_vz + (1-i) * p2_vz
                p2_vx = i * p1_vx + (1 - i) * p2_vx
                # print(p2_vz)



            vertices += [h_offset + (p1_vx / p1_vz) * horizontal_ratio,
                         v_offset + (wall_height / p1_vz) * vertical_ratio,
                         h_offset + (p1_vx / p1_vz) * horizontal_ratio,
                         v_offset - (character_height / p1_vz) * vertical_ratio,
                         h_offset + (p2_vx / p2_vz) * horizontal_ratio,
                         v_offset - (character_height / p2_vz) * vertical_ratio,
                         h_offset + (p2_vx / p2_vz) * horizontal_ratio,
                         v_offset + (wall_height / p2_vz) * vertical_ratio]

            # lines +=

        # for p in flying_vertexes:
        # pyglet.gl.glColor3f(0, 0, 0)
        pyglet.gl.glColor3f(.13, .7, .3)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                             ('v2f', (0, 0, width, 0, width, height/2, 0, height/2)))

        pyglet.gl.glColor3f(0, .63, .91)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                             ('v2f', (0, height / 2, width, height / 2, width, height, 0, height)))

        # pyglet.gl.glColor3f(0.3, 0.3, 0.3)
        pyglet.gl.glColor3f(.5, .5, .5)
        pyglet.gl.glLineWidth(wall_size)
        pyglet.graphics.draw(int(len(vertices)/2), pyglet.gl.GL_QUADS,
                             ('v2f', tuple(vertices)))
        pyglet.gl.glColor3f(0, 0, 0)
        # pyglet.gl.glColor3f(1, 1, 1)
        # print(len(vertices), len(walls))
        for i in range(int(len(vertices)/8)):
            pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
                                 ('v2f', tuple(vertices[8*i:8*(i+1)])))
        flying_vertexes2 = []
        for p in flying_vertexes:
            # print(type(p))
            # p = Vec2(*p)
            if p.dot(v1) > 0:
                flying_vertexes2 += [h_offset + (p.dot(v2) / p.dot(v1)) * horizontal_ratio,
                                     v_offset + (wall_height / p.dot(v1)) * vertical_ratio,
                                     h_offset + (p.dot(v2) / p.dot(v1)) * horizontal_ratio,
                                     v_offset - (character_height / p.dot(v1)) * vertical_ratio]
        pyglet.graphics.draw(int(len(flying_vertexes2)/2), pyglet.gl.GL_LINES,
                             ('v2f', tuple(flying_vertexes2)))

    else:
    # if True:

        for w in walls:
            lines += [w[0].x + h_offset, w[0].y + v_offset,
                      w[1].x + h_offset, w[1].y + v_offset]
            triangles += [h_offset, v_offset,
                     w[0].x + h_offset, w[0].y + v_offset,
                     w[1].x + h_offset, w[1].y + v_offset]
        for w in void_walls:
            triangles += [h_offset, v_offset,
                          w[0].x + h_offset, w[0].y + v_offset,
                          w[1].x + h_offset, w[1].y + v_offset]

        void_lines = []
        offset = Vec2(h_offset, v_offset)
        for v in flying_vertexes:
            dots += [*(v + offset)]
            void_lines += [*(offset + v), *(offset + v.normalized() * max(h_offset, v_offset))]
        if print_grey_lines:
            grey_lines2 = []
            for w in grey_lines:
                grey_lines2 += [w[0].x + h_offset, w[0].y + v_offset,
                              w[1].x + h_offset, w[1].y + v_offset]

        pyglet.gl.glColor3f(0.3, 0.3, 0.3)
        pyglet.graphics.draw(len(walls+void_walls) * 3, pyglet.gl.GL_TRIANGLES,
                             ('v2f', tuple(triangles)))
        if print_grey_lines:
            pyglet.gl.glColor3f(0.5, 0.5, 0.5)
            pyglet.graphics.draw(len(grey_lines)*2, pyglet.gl.GL_LINES,
                                 ('v2f', tuple(grey_lines2)))
        pyglet.gl.glColor3f(1, 1, 1)
        pyglet.gl.glLineWidth(wall_size)
        pyglet.graphics.draw(len(walls) * 2, pyglet.gl.GL_LINES,
                             ('v2f', tuple(lines)))
        pyglet.gl.glPointSize(wall_size)
        pyglet.gl.glColor3f(0, 0, 0)
        pyglet.graphics.draw(int(len(void_lines)/2), pyglet.gl.GL_LINES,
                             ('v2f', tuple(void_lines)))



        pyglet.gl.glColor3f(1, 1, 1)
        # pyglet.graphics.draw(len(flying_vertexes), pyglet.gl.GL_POINTS,
        #                      ('v2f', tuple(dots)))
        print(dots)
        pyglet.graphics.draw(len(dots)//2, pyglet.gl.GL_POINTS,
                         ('v2f', tuple(dots)))



        pyglet.gl.glPointSize(char_size)
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                             ('v2f', (h_offset, v_offset)))


pyglet.clock.schedule_interval(f, 1/120.0)
# pyglet.clock.set_fps_limit(60)
pyglet.app.run()


