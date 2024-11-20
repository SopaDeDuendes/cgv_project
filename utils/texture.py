from OpenGL.GL import *
from OpenGL.GLU import *

import pygame as pg

class Texture:
    def __init__(self, path):
        pg.init()
        self.texture_id = self.load_texture(path)

    def load_texture(self, path):
        texture_surface = pg.image.load(path)
        texture_data = pg.image.tostring(texture_surface, "RGBA", 1)
        width, height = texture_surface.get_size()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture_id