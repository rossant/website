# A compiler infrastructure for data visualization

We're seeing new big data tools every day now. There are tens or hundreds of data visualizations libraries out there. Yet I believe we're still lacking a robust, scalable, and cross-platform visualization toolkit that can handle today's massive datasets.

You'll always find excellent tools on all platforms, especially on the web, for little plots with a few hundreds of points, statistical charts like bar plots, histograms, scatter plots and the like. Maps are also extremely popular, and there are now really great open source tools, notably those by Mapbox.

It seems to me that, for many people, this is the end of the story. Maybe 90%, 95%, even more, of data visualization use cases are covered by these sorts of plots and these libraries.

Yet, there are more complex visualization needs in academia and industry, and I've always been unsatisfied by the tools at our disposal.

## Complex visualizations

To be more concrete, here are a few examples of the kinds of visualizations I'll be talking about throughout this post:

TODO

These are not dumb scatter plots. They are complex visualizations of large datasets with elaborate interactivity patterns. You're not going to implement these sorts of visualizations with SVG and D3. There are two main problems.


### Performance

The first problem is speed: things are going to be way too slow and memory-intensive. You might crash your browser or your computer because you're just plotting way more points than what your library can handle.

An often-heard counter-argument is that you're never going to plot millions of points where you only have a few million pixels on your screen. This is true when you're plotting aggregates like statistical quantities. But this is not as soon as you visualize complex, raw, unstructured datasets, like the ones you may find in some scientific and industrial applications.

To give only one example in the discipline I know: neurophysiologists can now routinely record in animals' brains thousands of simultaneous digital signals sampled at 20 kHz. That represents at least 20 million points *per second*. Recordings can last several hours or days. High-density 4k screens can now contain about 10 million pixels, maybe several times more in a few years. The scientists I know absolutely *do* want to visualize as much data as possible. They may have two, three, even four HiDPI screens, and they're eager to see all signals in a given time interval, as much as their screens' resolution allows (and they're starting do to it with the visualization prototypes we're developing). This is an unprecendent opportunity to really *see* what's going on in the brain. They're incredibly excited by this opportunity. The reason why very few people do that at the moment is that the tools are not quite there yet (apart from early prototypes). This is an example where the user absolutely needs to look at the raw data, not some aggregates, because they wouldn't even know what to aggregate. This is basically uncharted territory, and the only chance they can have to get some scientific insight in the data is to look at the raw data directly.

I am convinced that the demand is real in neuroscience, genomics, astronomy, particle physics, meteorology, finance, and many other scientific and industrial disciplines.

![That's many screens you've got here](http://www.timothysykes.com/wp-content/uploads/2011/04/desk.jpg)


### 3D

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

Also, I'm now thinking that the whole "pure Python" thing is a bit overrated. None of the main scientific Python libraries (NumPy, SciPy, matplotlib, scikit-learn, pandas) is in pure Python. What does "pure Python" even mean, really? VisPy calls the OpenGL C API through ctypes: is it "pure Python"? Also, you could even argue that a "pure Python" program is being interpreted by CPython, which is all written in *C*... Finally, there are other great data analysis platforms out there that could potentially benefit from advanced visualization capabilities, like Julia, R, etc. That's not something you could do with a pure Python library.

Another problem comes from VisPy itself. VisPy implements a powerful but complex system for managing transformations between objects in a scene. Because it is in pure Python, there always have been significant performance issues. This is a critical problem in a high-performance visualization library that needs to process huge datasets in real time. These issues are now getting mitigated thanks to heroic efforts by Luke Campagnola. But it should come as no surprise that achieving high performance in a pure Python library is highly challenging. Spending so many efforts just for the sake of being "pure Python" is not worth it in my opinion.

Finally, the most important problem with being pure Python comes from a design goal that came slightly after the project started. We wanted to support the web platform as well as Python thanks to **WebGL**, the browser's implementation of OpenGL. The web platform is now extremely popular, even in the scientific community via the Jupyter notebook. Many data visualization libraries (like D3, Bokeh) are built partly or entirely on the web platform. More and more video games and game engines are being ported to WebGL. Given the efforts spent by the industry, I really believe that this trend will continue for many years.

How do you make Python work in the browser? The browser's language is JavaScript, a language fundamentally different from Python. I've been obsessed by this question for a few years. I've explored many options. Unfortunately, none of them is really satisfying. Now, **my conclusion about Python in the browser is that it's never gonna happen**, at least not in the way you might think (more on this later).

There is a similar issue with mobile devices. Sadly, apart from the excellent Kivy project, Python on mobile devices is getting very little attention, and I'm not sure that's ever going to change. Yet, there would be a huge interest in semi-automatically creating mobile applications from data visualizations made for the desktop.

I believe these are fundamental problems about Python itself, that, in the case of VisPy, cannot be satisfactorily solved with our current approach. We do have temporary solutions for now, VisPy does have an experimental WebGL backend that works in the Jupyter notebook, but it is fundamentally *experimental*. Because of the WebGL support, we need to stick with the lowest common denominator between the desktop and the browser. This means we cannot support recent OpenGL features like geometry shaders, tesselation shaders, or compute shaders. These issues are at odds with the idea of designing a solid codebase that can be maintained over many years.


### Python and OpenGL

Another fundamental problem comes from OpenGL itself.

Modern OpenGL features a GPU-specific language named GLSL. GLSL is a C-like language that has nothing to do with Python. We believe that scientists should never have to write their own GPU code in a C dialect. Therefore, in VisPy, we try to hide GLSL completely to the user.

To make this possible, we need to bridge the gap between Python and GLSL. The graphics driver typically converts GLSL strings on-the-fly for the GPU. In VisPy, we have no other choice than generating GLSL strings dynamically. We do this with string templates, regular expressions, parsers and so on. We have a large collection of reusable GLSL components (notably contributed by Nicolas Rougier) that are put together automatically as a function of what the user wants to visualize. Designing and implementing a modular API for this was extremely challenging, and as a consequence the code is quite complex. Again, this complexity is inherent to OpenGL and to our desire to generate visualizations on-the-fly with a nice high-level Python API.

There are many other problems with OpenGL. There are many bugs in the drivers, depending on the graphics card's manufacturer. These bugs are hard to debug, and they need to be worked around with various hacks in the code. Memory accesses in the shaders are limited. Interoperability with GPGPU frameworks like CUDA and OpenCL are possible in practice, but so hard and buggy that it's not even worth trying. OpenGL's API is extremely obscure, and we need to hide this in the code through a dedicated abstraction layer. OpenGL has accumulated a lot of technical debt over the last 25 or so years. Everyone in the OpenGL community is well aware of the issue.

This is one of the cases where you get the feeling that the technology is working against you, not with you. And there's absolutely nothing you can do about it: it's just how things work.


### OpenGL's future?

All of this explains why I was so incredibly excited by the announcement made by the Khronos Group in March. They acknowledged that OpenGL was basically doomed, and they decided to start from scratch with a brand new low-level API for real-time graphics named **Vulkan**.

In my opinion this is just the best decision they could have ever made.

Compared to OpenGL, Vulkan is closer to the metal. It is designed at a different level of abstraction. Graphics drivers for Vulkan should be simpler, lighter and, hopefully, less buggy than before. Consequently, applications will have much more control on the graphics pipeline, but they'll also need to implement many more things, notably memory management on the GPU.

A major feature of the new API is **SPIR-V**, an LLVM-like intermediate language for the GPU. Instead of providing shaders using GLSL strings, graphics applications will have the possibility to provide low-level GPU bitcode directly. There should be tools to translate LLVM code to SPIR-V and reciprocally.

OpenGL and GLSL will still work as before through some conversion layers for obvious retrocompatibility reasons. There will be tools to compile GLSL code to SPIR-V. But applications won't have to go through GLSL if they don't want to.

This might just be the perfect solution for VisPy. Instead of mixing two different languages (Python and GLSL) with strings, templates, regexes, lexers and parsers, we could design a **compiler architecture for data visualization around LLVM and SPIR-V**.

Shaders and GPU kernels will no longer have to be written in GLSL; the can be written in **any language that can be compiled down to LLVM** (and, as a consequence, to SPIR-V). This includes low-level languages like GLSL and C/C++, but also Python thanks to **Numba**. Numba can compile an increasing variety of pure Python functions to LLVM. The primary use-case of Numba is high-performance computing, but it could also be used to write GPU kernels for visualization.

This could remove a huge layer of complexity in VisPy.

It might also be a solution to the cross-platform problems. We could potentially port visualizations to the browser by compiling them to JavaScript thanks to emscripten, or to mobile devices thanks to LLVM compilers for Android and iOS.

I'd now like to open the discussion on what a future Vulkan-vased data visualization toolkit could look like, on what use-cases it could enable. I should precise that everything that comes next is kind of speculative and depends on very partial information released by the Khronos group on early specification drafts. Also, I am well aware that this is a really ambitious and optimistic vision that might just be too hard to implement. But I believe it is worth trying.

Before we see in more details how all of this could work, let's describe a hypothetical data visualization use-case that could come true with Vulkan.


## Use-case example

There is a new data analysis pipeline that is going to process terabytes of data, and you're in charge of writing the analysis and visualization software. Your users have highly specific visualization needs. They want a fast, reactive, and user-friendly interface to interact with the data in various and complex ways.

You start to design a visualization prototype in the Jupyter notebook around your data. Through a Python API, you carefully design how to process and visualize the data on the GPU. This is not more complicated than creating a NumPy ufunc in pure Python with Numba: it's really the same idea of stream processing, but in a context of data visualization.

As part of this process, you also integrate interactivity by specifying how user actions (mouse, keyboard, touch gestures) influence the visualization.

At this point, you can embed your interactive visualization in a desktop Python application (for example with PyQt).

Now, your users are happy, they can visualize their data on the desktop, but they want more. They want a web interface to access, share, and visualize their data, all in the browser. The way it would happen today is that you'd hire one or two web developers to reimplement all your application in JavaScript and maybe WebGL. Now, you have two implementations of the same applications, in two different languages, for two different platforms.

I believe we can do better.

You go back to your Python visualization. Now, instead of running it interactively, you *compile* it automatically to a platform-independent bitcode file. Under the hood, this uses the LLVM platform. You get a binary file that implements the entire logic of your interactive visualization. This includes the GPU kernels, the rendering flow, and (possibly) interactivity. In a way, this is similar to running a C++ program generating a function dynamically via the LLVM API, versus compiling a function to an LLVM bitcode file.

Once you have this file, you start writing your web application in HTML and JavaScript (maybe using some of the future Jupyter notebook components). But instead of reimplementing the whole visualization and interactivity logic, you compile your exported file to JavaScript via emscripten. You then have your whole interactive visualization in the browser practically for free.

Of course, this will only work if Vulkan is eventually ported to the browser. There are no such plans yet, Vulkan being such an early project at this point, but I suppose it will depend on the user demand.

Now, your users are even happier, but they want even more. They want a mobile application for visualizing their data interactively. Again, you could compile your platform-independent visualization file to Android or iOS (both platforms are LLVM backends). Or maybe, who knows, mobile browsers will support Vulkan at some point, so your web application will just work!

Depending on your use-cases, the rest of the analysis pipeline can very well be implemented server-side in any language, like Python (potentially using Jupyter notebook components). It could even involve a cloud engine like Spark. The visualization logic could remain client-side, but you might have to implement custom level-of-detail techniques adapted to your data.


## Architecture

What would it take to make this use-case a reality?

There are several components:

* A Python API for creating interactive visualizations
* An engine that compiles visualizations to platform-independent files
* A runtime that executes visualizations specified via the Python API or via compiled files

### Language

In what cross-platform language could we implement these components? Python is not really an option because it cannot run on the browser or mobile devices.

I believe that a sensible option would be **modern C++** (typically C++ 11).

I used to dislike old-style C++, however I discovered in C++ 11 a really different language. It is modern, safe, mature, it has a wide community and solid documentation. The standard library looks reasonably powerful and well-designed.

C++ 11 can be compiled on many architectures, including JavaScript through the LLVM-based emscripten project. It seems to be well-supported on mobile devices as well. It is worth noting that the LLVM API itself is implemented in C++.

Of course, there may be other choices.

Obviously, choosing a relatively low-level language like C++ doesn't mean that end-users will have to write a single line of C++. There could be a Python library wrapping the C++ engine via ctypes, cffi, Cython, or something else. This is not really different from wrapping OpenGL via ctypes. Instead of leveraging a graphics driver that we cannot control at all, we use a C++ library on which we have full control.

I imagine that both the compiler and the runtime could be implemented in C++, and ported to the browser and mobile platforms via the LLVM toolchain.


### Library of functions

The compiler and runtime are just the core components. Then, to make the users' lives easier, we'd have to implement a rich library of functions, visuals, interactivity routines, and high-level APIs. Having a highly modular architecture is critical here.

There could be a rich user-contributed library of reusable pure functions:

* geometric transformations: linear, polar, logarithmic, various Earth projections, etc.
* color space transformations and colormaps
* easing functions for animations
* special mathematical functions
* linear algebra routines
* geometric tests
* classical mechanics equations
* common optics and lighting equations
* antialiasing routines
* common markers
* font generators with signed distance functions

Most of these could be written in any language that compiles to LLVM. This includes C/C++, GLSL, but also Python via Numba, making user contributions much easier.

I should note that VisPy already implements many of these functions in Python or GLSL, so we could reuse a lot of code.


### Memory model

Vulkan gives applications a lot of freedom regarding memory management. Therefore, we should come up with a simple yet powerful memory model that handles CPU-GPU transfers efficiently. One possibility could be to implement a NumPy-like ndarray structure that lives on both the CPU and GPU. It would be automatically and lazily synchronized.

This is the option chosen by **Glumpy**, VisPy's sister project maintained by Nicolas Rougier. VisPy uses a more complex memory model where data can be stored on the GPU only; while this might save some RAM, it is more complicated to work with this model. Also, the host has typically much more RAM than the GPU.

SPIR-V has a nice support for arbitrarily complex data types, and a NumPy-like API could be used.

One significant advantage of Vulkan and SPIR-V over OpenGL is that the framework encompasses OpenCL-like GPGPU routines as well as visualization shaders. Therefore, it would be possible to execute complex computation kernels on the same GPU data structures that are used for visualization, with no copy involved at all. Typical examples include real-time visualization of numerically-simulated systems like fluids, n-body simulations, biological networks, and so on.


### Higher-level APIs

All of this represents the core of a relatively low-level data visualization toolkit. A core that would let you create powerful and scalable interactive visualizations in any language, on any platform, and with optimal performance.

On top of this, we could imagine plotting libraries with various programming interfaces. The hypothetical core I've been describing would be a sort of "game engine, but for data visualization".


## Advantages

This vision represents a significant departure from the current state of the project. As a summary, I list here the advantages of choosing this path.


### Future-proof



### Truly cross-platform



### Modular and extendable architecture



### A "pure Python" end-user experience



### Access to modern GPU features



### Optimal performance



### High-performance GPGPU-powered visualizations



## Risks



