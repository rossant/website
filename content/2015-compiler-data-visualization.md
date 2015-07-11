# A compiler infrastructure for data visualization

Despite being more than two years old, VisPy is still in a relatively experimental stage. We knew from day one it would be a hard project. Personally, I wouldn't have thought it would be *that* hard. Yet, it doesn't have to be that hard. Why is it so hard?

I believe that the main problem is OpenGL itself, and its associated GPU language, GLSL. GLSL is a C-like language that has nothing to do with Python. In VisPy's higher-level layers, we try to hide GLSL to the user completely. Scientists should never have to write their own GPU code in a C dialect for routine scientific visualizations.

To make this possible, we need to bridge the gap between Python and GLSL. The way OpenGL works is that it accepts a GLSL string, the driver compiles it and sends it to the GPU. This is all handled by the graphics driver. So all we have to do is to generate GLSL strings dynamically. We do this with string templating, regular expressions, parsers, and so on. We have a collection of reusable GLSL components that we can reassemble dynamically when building visuals. A significant part of the library relies on this.

This brings quite some complexity in the code.

Things get even trickier with transformations.

The main benefit of the GPU for fast visualization is to perform dynamic data transformations on the GPU. For example, when zooming in a plot, a GPU kernel written in GLSL multiplies by a coefficient the data points residing in a GPU buffer. This is incredibly fast, because that's what GPUs are designed for.

However, there are many cases where we need to access the data on the CPU. For example, point picking, or selecting points with a lasso. Since the transformations are done on the GPU, we need a way to get the actual transformed point positions on the CPU.

OpenGL's way of doing it is quite hackish. It boils down to rendering the scene a second time in a hidden buffer with a unique color for every pickable object, getting the color rendered at the mouse position, and retrieving the associated object.

Another possibility is to implement the *inverse* transformation in Python. This means that every transformation needs to be implemented in GLSL *and* Python, and similarly for its inverse. This leads to some duplication of code.

So we need a framework to define, manipulate, and combine transformation functions that are implemented on both the CPU and the GPU.

This adds another layer of complexity.

Let's mention further sources of difficulty:

* We have to deal with the many quirks and bugs of the various OpenGL implementations by the different GPU manufacturers. OpenGL is overly complicated, and a lot of work is the responsability of the drivers. When a driver has a bug, we can either work around it with some hack in our code, or pray that a newer version of the driver will fix the bug in the future.

* GLSL kernels are quite limited in terms of memory access and computations, compared to GPGPU frameworks like CUDA or OpenCL. OpenGL-OpenCL interoperability is possible but extremely hackish, buggy, and driver-dependent. Yet, many applications would highly benefit from real-time GPGPU computations in a visualization application (for example, simulations of physical systems).

* One of VisPy's goals is to allow for interactive visualizations to work in the browser as well as on the desktop. We have a client-server architecture where OpenGL commands are streamed from Python to the browser and rendered by WebGL. Again, the architecture is complex, hard to debug, and requires a live Python server. An entire client-side implementation of an interactive visualization would be much appreciated, but we have no way to run VisPy in the browser (VisPy is written in Python and NumPy, which don't run in the browser).

This is what is currently implemented in VisPy, thanks to the heroic efforts of Luke, Almar, Eric, and the other contributors.

All of this explains why I was so incredibly excited by the Vulkan announcement in March. The Khronos Group acknowledged the debt accumulated in OpenGL by almost 25 years of development. They decided to start basically from scratch with a brand new, modern, modular low-level API.

Compared to OpenGL, Vulkan is lower-level, closer to the metal, and demands more from applications. Consequently, drivers will be expected to be much lighter, and hopefully much less buggy.

A major feature of the new API is SPIR-V, a LLVM-like intermediate language for GPU kernels. While Vulkan will provide a GLSL-to-SPIR-V compiler (and probably LLVM <-> SPIR-V translators too), third-party applications will have the liberty to implement their own compilers. Potentially, this paves the way for GPU computing and graphics implementations in high-level languages like Python (thanks to projects like Numba).

This might just be the perfect solution for VisPy. Instead of mixing two different languages (Python and GLSL), we could design a compiler architecture around LLVM and SPIR-V. Instead of designing a complex GLSL code generation system in Python, we could just write GPU kernels in Python, or in any other language. Instead of implementing transformations in both Python and GLSL, we could implement them in any language that compiles to LLVM. In other words, we have an opportunity to design a GPU-aware compiler architecture for interactive visualization that could natively support high-level languages like Python.

In this post I'll sketch some ideas about how an ideal low-level data visualization toolkit based on Vulkan could look like. By low-level, I mean a system that targets developers of high-level graphics libraries (for example, plotting libraries, ray tracing engines, etc.).


## Objectives

What would I expect from an ideal low-level data visualization tookit?

**Speed**. Of course, that's the primary goal of a GPU-based visualization framework. I'd expect the software to display tens or hundreds of millions of points at full speed, i.e. 60 FPS.

**Flexibility**. I'd want to use the same framework and API for 2D plots, complex 3D viewers, demoscene-like animations, *processing*-like data visualizations, d3-like graphs, little video games, etc.

**Modularity**. I'd want to reuse some existing visuals and combine them with my own visuals, all written in my language of choice.

**Cross-platform**. If I write a complex visualization application, I'd want to use it on my desktop, share it online, and develop a mobile app around it.

**Cross-languages**. If I'm working in Python, I'd expect to write 100% of my visualization code in pure Python, and have a way to run it in the browser and on mobile devices. This may require some platform-specific development efforts, but most of the visualization code wouldn't need to be rewritten. Further, there's no reason to stick with Python: the library could work with other languages like Julia, R, or even MATLAB.

**Exportable**. I'd want to export my visualization to EPS, PDF, SVG, PNG, videos, etc.

**Cloud-friendly**. If I'm analyzing some data in the Jupyter notebook with Spark, I'd want to visualize huge amounts of data interactively in the browser (client-side or server-side rendering, depending on the use-cases).

**High-density-screens-friendly**. Because too many people have Retina MacBooks.

* **CPU fallback**. I'd want to run my visualization on the CPU if the GPU is not available or not powerful enough. That would also be convenient for automated testing, debugging, etc.

That's about it. That's very ambitious, but I think that, with technologies like Vulkan, SPIR-V, and LLVM, we'll have all the tools we need to achieve these goals.


## Use-cases

Let's see a few examples of typical visualizations or end-user applications that could work with this hypothetical library:

* A boring 2D plot with full support for high-quality markers, axes, LaTeX labels, ticks, grids, smooth panning and zooming (scales to tens or hundreds of millions of points). A set of points can be selected by dragging a box or a lasso. That seems trivial, but it took us 2.5 years to get to this point in VisPy.

* A digital acquisition system that can display thousands of real-time animated signal with zmooth panning and zooming.

* A high-resolution dynamic fractal viewer with smooth panning and zooming and variable parameters. The fractal is entirely rendered on the GPU.

* A visualizer of an arbitrarily complex 3D model, with a trackball camera, selectable components, full transparency support, dynamic lighting, etc.

* An animated force-directed layout of a network containing millions of nodes and edges, with smooth panning and zooming. Nodes should be individually selectable.

* A real-time POV-like ray-tracing engine, or a shadertoy-like animation that is entirely implemented in the fragment shader.

* A fast photo/video viewer or a slideshow presenter with animated transitions.

I should note that most if not all of these examples are already possible with VisPy. However, performance is suboptimal, the API is still changing, the code is complex and hard to maintain, and it is based on an aging 25-years-old technology. Vulkan is an opportunity to design a framework on much saner bases.


## Language

The cross-platform and cross-languages objectives put strong constraints on the development languages. We know we'd like to use Vulkan, SPIR-V, and LLVM. On the backend side, we'd like to target the desktop, the browser, and mobile devices. On the frontend side, we'd like to support high-level languages like Python, Julia, R, Lua, MATLAB, and many others, potentially. What language could we possibly use for the library itself?

I think that C++ 11 would be a compelling solution. I was used to dislike old-style C++, however I discovered in C++ 11 a significantly different (in the positive meaning) language. It seems to be a modern, safe, and appreciated language, with a wide community and solid documentation. The standard library looks reasonably powerful and well-designed.

C++ 11 can be compiled on many architectures, including JavaScript through the LLVM-based emscripten project. As far as I know, it is supported on mobile devices as well. Finally, the LLVM API itself is written in C++.

There may be other choices as well.

The core of the library being written in C++ wouldn't mean that users would have to write a single line of C++, of course. The whole point of the library is to design an architecture where a visualizations can be defined in any language, and compiled through C++ into a language-independent representation.


## Standard library of LLVM functions

The library would come with a large base of reusable functions: geometric transformations and their inverses (linear, polar, logarithmic, various Earth projections, etc.), color space transformations and colormaps, easing functions for animations, special mathematical functions, linear algebra algorithms, geometric tests, physics equations for lighting, optics, mechanics, algorithms for antialiasing, AGG rendering, font rendering with signed distance functions, contours of common markers, etc.

These functions could be originally written in any language that compiles to LLVM (C/C++, Python, GLSL, etc.); they'd be compiled to the LLVM IR and stored as binary `.bc` (bitcode) files in some directory. This would provide a solid basis for all kinds of visuals. These functions could run on the CPU thanks to the LLVM library, and on the GPU thanks to the hypothetical LLVM-to-SPIR-V translator that would be provided by Khronos.

The richness of the library would actually come from the wide range of built-in functions. Many advanced visuals could be written without too much efforts by combining several of these fuctions. Most of these functions would be automatically vectorized on GPUs for optimal performance.

Users could implement their own functions in the language of their choice; they'd be compiled to LLVM at runtime. In Python, the Numba library could be used for this.


## Data arrays

The library would provide a simple memory model. For example, NumPy-like N-dimensional arrays could be represented on both the CPU and GPU. The data would be automatically and lazily synchronized between the two.

This is how Glumpy works (VisPy's sister project), but not VisPy. VisPy uses a more complex memory model where data can be stored on the GPU only; this saves host RAM when using large datasets, but it is a less convenient model to work with. The host has typically much more RAM than a GPU, so I think the convenience of not having to deal with manual CPU-GPU transfers wins over saving some RAM.

SPIR-V has a nice support for complex data types. As far as I understand, data types are defined recursively from a few primitive types, and any C structure could be used.

LLVM kernels would have a way to address any location in an array, but the procedure might be different between compute and graphics kernels. Also, one would need to be aware of coalesced memory accesses in order to achieve better performance. Finally, there could be a way for kernels to access shared memory and to implement memory fences (SPIR-V will support this).


## Visuals

Visuals form a major abstraction in VisPy. It represents any object that is part of the scene. A visuals exposes a set of public attributes and methods. For example, a `DiscVisual` would expose a radius, line width, and background and foreground colors.

In addition, a visual holds some internal data; typically, CPU-GPU-synchronized ndarrays. For example, the disc visual could compute and store the vertices defining the circular edge. The number of vertices would depend on the disc's radius.

Finally, a visual implements a drawing method that renders it in a given coordinate system, using a handful of primitive rendering methods. The Vulkan API specification has yet to be released, but I imagine it could work like this (this is probably highly simplified):

* acquire the ndarrays you're going to use (using something like a `with` context in Python)
* generate N vertices
* call some compute and graphics kernels (vertex, geometry, tesselation, fragment shaders)
* render with a given primitive type (point, line, triangle)

A visual would have full control on the command buffer for rendering.

The C++ API would provide a dynamic visual builder; users of high-level languages could implement a visual in the language of their choice, and the library would compile it at runtime.


## Coordinate systems

There would be a few predefined coordinate systems: normalized coordinates (-1, 0, 1) and device-independent pixels (width, height). Further custom coordinate systems could be defined by the user; they would have a name, and a set of transformation functions with respect to existing coordinate systems. The transformation from any coordinate system A to another sytem B could be computed from the graph of dependences.

The API could let the user decide how to render the visuals.


## Interactivity

As for visuals, interactivity could be written in any language and compiled to machine code via LLVM. An alternative possibility would be to implement the interactivity logic in a high-level language and let the interpreter run it.

Interactivity functions would have access to user input variables (mouse positions, key pressed) and the ndarrays.
