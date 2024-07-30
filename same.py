import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import noise
import tkinter as tk
from tkinter import ttk
import os

def generate_heightmap(width, height, scale, octaves, persistence, lacunarity):
    height_map = np.zeros((width, height))
    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            height_map[x][y] = noise.pnoise2(nx, ny, octaves=octaves, persistence=persistence, lacunarity=lacunarity) * 10  # Adjust scaling factor as needed
    return height_map

def generate_vertices(heightmap, heightmap_size, scale_factor):
    vertices = []
    tex_coords = []
    origin = (-heightmap_size[0] / 2, 0, -heightmap_size[1] / 2)

    min_height = np.min(heightmap)
    max_height = np.max(heightmap)

    step_x = scale_factor / (heightmap_size[0] - 1)
    step_y = scale_factor / (heightmap_size[1] - 1)

    for x in range(heightmap_size[0]):
        for y in range(heightmap_size[1]):
            x_coord = origin[0] + step_x * x
            y_coord = 50 * (heightmap[x][y] - min_height) / (max_height - min_height)  # Normalize heights
            z_coord = origin[2] + step_y * y
            vertices.append((x_coord, y_coord, z_coord))
            tex_coords.append((x / (heightmap_size[0] - 1), y / (heightmap_size[1] - 1)))

    return vertices, tex_coords

def generate_tris(grid_size):
    tris = []
    for x in range(grid_size[0] - 1):
        for y in range(grid_size[1] - 1):
            index = x * grid_size[1] + y
            a = index
            b = index + 1
            c = index + grid_size[1] + 1
            d = index + grid_size[1]
            tris.append((a, b, c))
            tris.append((a, c, d))
    return tris

def calculate_normals(vertices, tris):
    normals = [np.zeros(3) for _ in range(len(vertices))]
    for tri in tris:
        v1, v2, v3 = [vertices[i] for i in tri]
        normal = np.cross(np.subtract(v2, v1), np.subtract(v3, v1))
        normal = normal / np.linalg.norm(normal)
        for i in tri:
            normals[i] += normal
    normals = [n / np.linalg.norm(n) for n in normals]
    return normals

def load_texture(texture_file):
    texture_surface = pygame.image.load(texture_file)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
    width, height = texture_surface.get_rect().size

    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id

def render_mesh(vertices, tris, normals, tex_coords):
    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)
    for tri in tris:
        heights = [vertices[i][1] for i in tri]
        average_height = sum(heights) / len(heights)

        if average_height < 10:
            glBindTexture(GL_TEXTURE_2D, water_texture)
        elif average_height < 15:
            glBindTexture(GL_TEXTURE_2D, sand_texture)
        elif average_height < 25:
            glBindTexture(GL_TEXTURE_2D, grass_texture)
        elif average_height < 35:
            glBindTexture(GL_TEXTURE_2D, rock_texture)
        else:
            glBindTexture(GL_TEXTURE_2D, snow_texture)

        glBegin(GL_TRIANGLES)
        for vertex_index in tri:
            glNormal3fv(normals[vertex_index])
            glTexCoord2fv(tex_coords[vertex_index])
            glVertex3fv(vertices[vertex_index])
        glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

def init_opengl(display_width, display_height):
    pygame.display.set_mode((display_width, display_height), DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))  # Infinite light
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)

    glViewport(0, 0, display_width, display_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, display_width / display_height, 0.08, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, camera_distance,
              0, 0, 0,
              0, 1, 0)

class TerrainGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Terrain Generator Parameters")

        self.scale_var = tk.DoubleVar(value=50)
        self.octaves_var = tk.IntVar(value=5)
        self.persistence_var = tk.DoubleVar(value=0.5)
        self.lacunarity_var = tk.DoubleVar(value=2.0)
        self.scale_factor_var = tk.DoubleVar(value=200)

        ttk.Label(master, text="Scale:").grid(row=0, column=0)
        ttk.Scale(master, from_=10, to_=100, variable=self.scale_var, orient="horizontal").grid(row=0, column=1)

        ttk.Label(master, text="Octaves:").grid(row=1, column=0)
        ttk.Scale(master, from_=1, to_=10, variable=self.octaves_var, orient="horizontal").grid(row=1, column=1)

        ttk.Label(master, text="Persistence:").grid(row=2, column=0)
        ttk.Scale(master, from_=0.1, to_=1.0, variable=self.persistence_var, orient="horizontal").grid(row=2, column=1)

        ttk.Label(master, text="Lacunarity:").grid(row=3, column=0)
        ttk.Scale(master, from_=1.0, to_=4.0, variable=self.lacunarity_var, orient="horizontal").grid(row=3, column=1)

        ttk.Label(master, text="Scale Factor:").grid(row=4, column=0)
        ttk.Scale(master, from_=100, to_=400, variable=self.scale_factor_var, orient="horizontal").grid(row=4, column=1)

        ttk.Button(master, text="Apply", command=self.update_parameters).grid(row=5, column=0, columnspan=2)

    def update_parameters(self):
        global scale, octaves, persistence, lacunarity, scale_factor
        scale = self.scale_var.get()
        octaves = self.octaves_var.get()
        persistence = self.persistence_var.get()
        lacunarity = self.lacunarity_var.get()
        scale_factor = self.scale_factor_var.get()
        regenerate_terrain()

def regenerate_terrain():
    global vertices, tris, normals, tex_coords, height_map
    height_map = generate_heightmap(width, height, scale, octaves, persistence, lacunarity)
    vertices, tex_coords = generate_vertices(height_map, height_map.shape, scale_factor)
    tris = generate_tris(height_map.shape)
    normals = calculate_normals(vertices, tris)

import os

def save_mtl(filename):
    try:
        with open(filename, 'w') as f:
            f.write("newmtl water\n")
            f.write("map_Kd water_texture.jpg\n")
            f.write("\n")
            f.write("newmtl sand\n")
            f.write("map_Kd sand_texture.jpg\n")
            f.write("\n")
            f.write("newmtl grass\n")
            f.write("map_Kd grass_texture.jpg\n")
            f.write("\n")
            f.write("newmtl rock\n")
            f.write("map_Kd rock_texture.jpg\n")
            f.write("\n")
            f.write("newmtl snow\n")
            f.write("map_Kd snow_texture.jpg\n")
            f.write("\n")
        print(f"MTL file saved: {filename}")
    except Exception as e:
        print(f"Failed to save MTL file: {e}")

def save_obj(filename, vertices, tex_coords, normals, tris):
    try:
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        mtl_filename = os.path.splitext(filename)[0] + '.mtl'
        save_mtl(mtl_filename)
        
        with open(filename, 'w') as f:
            f.write(f"mtllib {os.path.basename(mtl_filename)}\n")
            
            for vertex in vertices:
                f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            for tex_coord in tex_coords:
                f.write(f"vt {tex_coord[0]} {tex_coord[1]}\n")
            for normal in normals:
                f.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")
            
            for tri in tris:
                heights = [vertices[i][1] for i in tri]
                average_height = sum(heights) / len(heights)
                
                if average_height < 10:
                    f.write("usemtl water\n")
                elif average_height < 15:
                    f.write("usemtl sand\n")
                elif average_height < 25:
                    f.write("usemtl grass\n")
                elif average_height < 35:
                    f.write("usemtl rock\n")
                else:
                    f.write("usemtl snow\n")
                    
                f.write(f"f {tri[0]+1}/{tri[0]+1}/{tri[0]+1} {tri[1]+1}/{tri[1]+1}/{tri[1]+1} {tri[2]+1}/{tri[2]+1}/{tri[2]+1}\n")
        print(f"OBJ file saved: {filename}")
    except Exception as e:
        print(f"Failed to save OBJ file: {e}")

def main():
    global width, height, scale, octaves, persistence, lacunarity, scale_factor
    global vertices, tris, normals, tex_coords, height_map, water_texture, sand_texture, grass_texture, rock_texture, snow_texture
    global camera_distance, camera_rotation_x, camera_rotation_y

    # Initial settings
    width, height = 200, 200
    scale = 50
    octaves = 5
    persistence = 0.5
    lacunarity = 2.0
    scale_factor = 200

    camera_distance = 500
    camera_rotation_x = 45
    camera_rotation_y = 45

    try:
        pygame.init()
        display = (600, 600)
        init_opengl(display[0], display[1])

        # Load textures
        water_texture = load_texture('water_texture.jpg')
        sand_texture = load_texture('sand_texture.jpg')
        grass_texture = load_texture('grass_texture.jpg')
        rock_texture = load_texture('rock_texture.jpg')
        snow_texture = load_texture('snow_texture.jpg')

        # Generate terrain
        regenerate_terrain()

        # Create GUI window for parameters
        root = tk.Tk()
        gui = TerrainGUI(root)
        root.update()

        # Main loop
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Handle camera rotation using arrow keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                camera_rotation_x -= 2
            if keys[pygame.K_RIGHT]:
                camera_rotation_x += 2
            if keys[pygame.K_UP]:
                camera_rotation_y -= 2
            if keys[pygame.K_DOWN]:
                camera_rotation_y += 2

            # Handle zoom using mouse scroll wheel
            zoom = pygame.mouse.get_rel()[1]
            camera_distance += zoom

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            gluLookAt(camera_distance * np.sin(np.radians(camera_rotation_x)),
                      camera_distance * np.sin(np.radians(camera_rotation_y)),
                      camera_distance * np.cos(np.radians(camera_rotation_x)),
                      0, 0, 0,
                      0, 1, 0)

            render_mesh(vertices, tris, normals, tex_coords)

            pygame.display.flip()
            clock.tick(30)
            root.update()

        # After exiting the main loop, save the terrain as OBJ
        obj_filename = 'C:\\Users\\shifa_4ilddm5\\Desktop\\Terrain Generator\\terrain.obj'
        save_obj(obj_filename, vertices, tex_coords, normals, tris)

    except Exception as e:
        print(f"Exception occurred: {e}")
        pygame.quit()
        raise

    pygame.quit()

if __name__ == "__main__":
    main()


