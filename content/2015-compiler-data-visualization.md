# A compiler infrastructure for data visualization

We're seeing new big data tools every day now. There are tens or hundreds of data visualizations libraries out there. Yet I believe we're still lacking a robust, scalable, and cross-platform visualization toolkit that can handle today's massive datasets.

You'll always find excellent tools on all platforms, especially on the web, for little plots with a few hundreds of points, statistical charts like bar plots, histograms, scatter plots and the like. Maps are also extremely popular, and there are now really great open source tools, notably those by Mapbox.

It seems to me that, for many people, this is the end of the story. Maybe 90%, 95%, even more, of data visualization use cases are covered by these sorts of plots and these libraries.

Yet, there are more complex visualization needs in academia and industry, and I've always been unsatisfied by the tools at our disposal.

To be more concrete, here are a few examples of the kinds of visualizations I'm talking about:

TODO

You're not going to implement these with SVG and D3. There are two main problems.


## Visualizing millions of points

The first problem is speed: things are going to be way too slow and memory-intensive. You might crash your browser or your computer because you're just plotting way more points than what your library can handle.

An often-heard counter-argument is that you're never going to plot millions of points where you only have a few million pixels on your screen. This is true when you're plotting aggregates like statistical quantities. But this is not as soon as you visualize complex, raw, unstructured datasets, like the ones you may find in some scientific and industrial applications.

To give only one example in the discipline I know: neurophysiologists can now routinely record in animals' brains thousands of simultaneous digital signals sampled at 20 kHz. That represents at least 20 million points *per second*. Recordings can last several hours or days. High-density 4k screens can now contain about 10 million pixels, maybe several times more in a few years. The scientists I know absolutely *do* want to visualize as much data as possible. They may have two, three, even four HiDPI screens, and they're eager to see all signals in a given time interval, as much as their screens' resolution allows (and they're starting do to it with the visualization prototypes we're developing). This is an unprecendent opportunity to really *see* what's going on in the brain. They're incredibly excited by this opportunity. The reason why very few people do that at the moment is that the tools are not quite there yet (apart from early prototypes).

I am convinced that the demand is real in neuroscience, genomics, astronomy, particle physics, meteorology, finance, and many other scientific and industrial disciplines.

![That's many screens you've got here](http://www.timothysykes.com/wp-content/uploads/2011/04/desk.jpg)


## 3D visualization

The second problem is 3D: most plotting libraries are designed for 2D, and when they support 3D, they don't do it well because 3D is implemented as an afterthought.

There are good 3D libraries out there, like three.js. But they're mostly designed to the main use-cases of 3D visualization: video games or modeling. Not data visualization. Your only option is to resort to very low-level tools like OpenGL, which no sane scientist will ever do.

Also, I believe that 3D is going to gain more and more traction in the coming years with the advances in 3D printing technology, virtual reality, augmented reality, etc. The same momentum might happen in data visualization as well.


## VisPy: where we are now

These are all the reasons why we've started the [**VisPy project**](http://vispy.org) more than two years ago. We wanted to design a high-performance visualization library in Python that would handle massive datasets well, and where 2D and 3D visualization would both be first-class citizens. The main idea of VisPy is to leverage the massively parallel graphics card through the OpenGL library for data visualization purposes.

VisPy now has half a dozen of core contributors and tens of occasional contributors. We've also reached the highly-respected milestones of 666 stars on GitHub.

However, I personally consider the project to be still in its infancy. There is still a whole lot of work before VisPy gets to a mature and stable state. If the [Jupyter developers admit considering the notebook (almost 5 years old, estimated 2 million users) as a "validated MVP" (Minimum Viable Product)](http://blog.jupyter.org/2015/07/07/project-jupyter-computational-narratives-as-the-engine-of-collaborative-data-science/), I can definitely see VisPy as a somewhat solid proof-of-concept/prototype. This might sound crazy, but it's really not. To give an idea, matplotlib, the state-of-the-art visualization library in Python, is almost 15 years old; Python and OpenGL are about 25 years old; UNIX was developed half a century ago; and so on and so forth. We like to consider software as a fast-paced environment, but, in many respects, time scales can be much slower than what we think.

What will it take to bring the project to the next level? What can we do to ensures it lives through the next 5, 10, even 15 years?


## Current challenges

If we're serious about this sustainability question, **I believe we need to rethink the entire logic of the project from scratch**. There are three main reasons.


### A pure Python cross-platform library?

From the very beginning, we wanted a pure Python library. We were all using Python for our research, and we had all developed our own OpenGL-based Python prototypes for data visualization. Performance was excellent in our respective prototypes. We weren't using any compiled C extension or Cython, because we didn't need to. We were able to leverage OpenGL's performance quite efficiently thanks to ctypes and NumPy. So we decided to go with a pure Python library.

One of the reasons was that we wanted to avoid compiled extensions at any cost. Packaging and distributing compiled Python libraries used to be an absolute pain. However, this is no longer the case thanks to Anaconda.

Also, I'm now thinking that the whole "pure Python" thing is a bit overrated. None of the main scientific Python libraries (NumPy, SciPy, matplotlib, scikit-learn, pandas) is in pure Python. What does "pure Python" even mean, really? VisPy calls the OpenGL C API through ctypes: is it "pure Python"? Also, you could even argue that a "pure Python" program is being interpreted by CPython, which is all written in *C*...

Another problem comes from VisPy itself. VisPy implements a powerful but complex system for managing transformations between objects in a scene. Because it is in pure Python, there always have been significant performance issues. This is a critical problem in a high-performance visualization library that needs to process huge datasets in real time. These issues are now getting mitigated thanks to heroic efforts by Luke Campagnola. But it should come as no surprise that achieving high performance in a pure Python library is highly challenging. Spending so many efforts just for the sake of being "pure Python" is not worth it in my opinion.

Finally, the most important problem with being pure Python comes from a design goal that came slightly after the project started. We wanted to support the web platform as well thanks to **WebGL**, the browser's implementation of OpenGL. The web platform is now extremely popular, even in the scientific community via the Jupyter notebook. Many data visualization libraries (like D3, Bokeh) are built partly or entirely on the web platform. More and more video games and game engines are being ported to WebGL. Given the efforts spent by the industry, I really believe that this trend will continue for many years.

How do you make Python work in the browser? The browser's language is JavaScript, a language that is fundamentally different from Python. I've been obsessed by this question for a few years. I've explored many options. Unfortunately, none of them is really satisfying. Now, **my conclusion about Python in the browser is that it's never gonna happen**, at least not in the way you might think (more on this later in this post).

There is a similar issue with mobile devices. Sadly, apart from the excellent Kivy project, Python on mobile devices is getting very little attention, and I'm not sure that's ever going to change. Yet, there would be a huge interest in a tool that could convert a visualization designed for the desktop into a mobile application.

I believe these are fundamental problems about Python itself, that, in the case of VisPy, cannot be satisfactorily solved with our current approach. We do have temporary solutions for now, VisPy does have an experimental WebGL backend that works in the Jupyter notebook, but it is fundamentally *experimental*. This is at odds with the idea of designing a solid codebase that can be maintained over many years.


### Python and OpenGL

Another fundamental problem comes from OpenGL itself.

Modern OpenGL features a GPU-specific language named GLSL. GLSL is a C-like language that has nothing to do with Python. We believe that scientists should never have to write their own GPU code in a C dialect. Therefore, in VisPy, we try to hide GLSL completely to the user.

To make this possible, we need to bridge the gap between Python and GLSL. The graphics driver typically converts GLSL strings on-the-fly for the GPU. In VisPy, we have no other choice than generating GLSL strings dynamically. We do this with string templates, regular expressions, parsers and so on. We have a large collection of reusable GLSL components (notably contributed by Nicolas Rougier) that are put together automatically as a function of what the user wants to visualize. Designing and implementing a modular API for this was extremely challenging, and as a consequence the code is quite complex. Again, this complexity is inherent to OpenGL and to our desire to generate visualizations on-the-fly with a nice high-level Python API.

There are many other problems with OpenGL. There are many bugs in the drivers, depending on the graphics card's manufacturer. These bugs are hard to debug, and they need to be worked around with various hacks in the code. Memory accesses in the shaders are limited. Interoperability with GPGPU frameworks like CUDA and OpenCL are possible in practice, but so hard and buggy that it's not even worth trying. OpenGL's API is extremely obscure, and we need to hide this in the code through a dedicated abstraction layer. OpenGL has accumulated a lot of technical debt over the last 25 or so years.

This is one of the cases where you get the feeling that the technology is working against you, not with you. And there's absolutely nothing you can do about it: it's just how things work.


### OpenGL's future?

















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
