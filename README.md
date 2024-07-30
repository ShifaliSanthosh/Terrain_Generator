# Terrain Generator

## Overview

This project is a procedural terrain generator that creates realistic 3D terrain models using Perlin noise. The generated terrains can be rendered in real-time with OpenGL and come with various biomes like water, sand, grass, rock, and snow based on height. Users can interact with the terrain in real-time and adjust generation parameters through a graphical user interface (GUI).

![Terrain Screenshot]![image](https://github.com/user-attachments/assets/84468eb9-6cd7-4c00-bac7-3f8214972d6b)
)

## Features

- **Heightmap Generation**: Uses Perlin noise to create detailed heightmaps for terrain.
- **Biome Texturing**: Applies different textures (water, sand, grass, rock, snow) based on terrain height.
- **Real-Time Rendering**: Renders the terrain in real-time using OpenGL.
- **Interactive GUI**: Allows users to adjust parameters such as scale, octaves, persistence, and lacunarity.
- **OBJ Export**: Saves the generated terrain as an OBJ file for use in other 3D applications.
- **Camera Controls**: Use arrow keys to rotate the camera and mouse scroll for zoom.

## Technologies Used

- **Python**: The core language used for development.
- **Pygame**: For handling windowing and input.
- **OpenGL (via PyOpenGL)**: For rendering the terrain.
- **Tkinter**: For the GUI to adjust terrain parameters.
- **NumPy**: For numerical operations.
- **Noise**: For generating Perlin noise.

## How It Works

The project generates a heightmap using Perlin noise, where each point on the heightmap is calculated based on noise values. This heightmap is then converted into a 3D mesh with vertices, texture coordinates, and normals. Different textures are applied to different height ranges to create the appearance of biomes.

### Heightmap Generation

- **Scale**: Determines the level of detail in the terrain.
- **Octaves**: The number of layers of noise added together to create detail.
- **Persistence**: Controls the amplitude of each octave.
- **Lacunarity**: Controls the frequency of each octave.

### Rendering

The terrain is rendered in OpenGL with different textures based on height:
- **Water**: For the lowest points.
- **Sand**: For slightly higher points.
- **Grass**: For mid-level points.
- **Rock**: For high points.
- **Snow**: For the highest points.
