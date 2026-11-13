import ctypes
import json
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

CELULA = 60
CORES = {0: (0.80, 0.72, 0.55), 1: (0.35, 0.35, 0.40), 2: (0.20, 0.60, 0.25), 3: (0.55, 0.25, 0.85)}

VERT = """#version 330 core
layout (location = 0) in vec2 pos;
layout (location = 1) in vec3 cor;
uniform vec2 tam;
out vec3 c;
void main() {
    vec2 p = pos / tam * 2.0 - 1.0;
    gl_Position = vec4(p.x, -p.y, 0.0, 1.0);
    c = cor;
}"""

FRAG = """#version 330 core
in vec3 c;
out vec4 saida;
void main() { saida = vec4(c, 1.0); }"""


def ler_mapa(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)["matriz"]


def desenhar_mapa(matriz):
    linhas, colunas = len(matriz), len(matriz[0])

    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    janela = glfw.create_window(colunas * CELULA, linhas * CELULA, "Mapa", None, None)
    glfw.make_context_current(janela)

    # Cada quadrado = 2 triângulos. Cada vértice = x, y, r, g, b
    b = 0.03  # borda que forma a grade
    vertices = []
    for i in range(linhas):
        for j in range(colunas):
            cor = CORES[matriz[i][j]]
            esquerda, direita = j + b, j + 1 - b
            topo, base = i + b, i + 1 - b

            vertices += [esquerda, topo, *cor,  direita, topo, *cor,  direita, base, *cor]  # triângulo 1
            vertices += [esquerda, topo, *cor,  direita, base, *cor,  esquerda, base, *cor]  # triângulo 2
    vertices = np.array(vertices, dtype=np.float32)

    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)

    programa = compileProgram(compileShader(VERT, GL_VERTEX_SHADER), compileShader(FRAG, GL_FRAGMENT_SHADER))
    glUseProgram(programa)
    glUniform2f(glGetUniformLocation(programa, "tam"), colunas, linhas)
    glClearColor(0.1, 0.1, 0.1, 1)  # cor da grade

    while not glfw.window_should_close(janela):
        glViewport(0, 0, *glfw.get_framebuffer_size(janela))
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 5)
        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()


desenhar_mapa(ler_mapa("mapas/mapa1.json"))
