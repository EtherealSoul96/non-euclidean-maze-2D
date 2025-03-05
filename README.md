# Non-Euclidean Maze 2D
Non-Euclidean maze generator that works by connecting triangles in arbitrary graph-like structures.

There is a variable called 'infinite' that you can set to True or False

If set to False, the program will use the variables 'n' and 'loops' to create a random finite non-Euclidean maze that has 'n' triangles and 'loops' loops.
If 'loops' is 0, every triangle will be connected through a unique path with every other triangle.
For every loop, the maze generator will include an extra connection, meaning you can take one path and return to the original place, which would be a different place if the maze was Eucldean (for example going up and right and endind up where you started), because of this, if the same triangle you are standing on is in sight, the result will be a recursive perspective where your position can be displayed in multiple places and with different rotations.

If set to True, the program will instead use the variable 'ratio' to randomly create a maze, where each triangle will have in average that amount of connections, this means that if the value is less than 2, the maze will tend to collapse, since in a finite maze (without loops) triangles will have in average almost 2 connections per triangle.
If set to 2 or more the maze will be infinite, which means that as you explore different paths, new ones will be created.
The way this program works is that everytime the program calculates the perspective of the player, it checks if there are any new sides that still have undefined status, in that case it randomly becomes a wall or a new triangle. the program also keeps track of every already determined connection, so if you go back the maze continues being the same.

The program also has an optional 3D perspective that is created by transforming the 2D walls (segments) into 3D walls (rectangles rendered as trapezoids), it manages that by calculating the 3D perspective and drawing the trapezoids with 2D triangles.

Controls:
* Move: a, w, s, d
* toggle 3D view: 3
* toggle fullscreen: f
