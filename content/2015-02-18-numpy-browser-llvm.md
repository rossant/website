Title: NumPy in the browser: proof of concept with Numba, LLVM, and emscripten
Tags: python

It's been a while since I wanted to try to bring some of NumPy to the browser. I've already discussed the motivations for this [in a previous post last year]({filename}2014-03-31-scientific-python-in-the-browser-its-coming.md). One of the main motivations as far as I'm concerned is to enable interactive visualizations in offline notebooks (including nbviewer). In this post, I'll describe a proof of concept where I successfully compile NumPy-aware Python functions to JavaScript using Numba, LLVM, and emscripten.

<!-- PELICAN_END_SUMMARY -->

How to bring NumPy to the browser? There are at least two quite different approaches.

The first approach consists of reimplementing a tiny subset of NumPy in JavaScript. Many computations can be implemented with a minimum feature set of NumPy: the ndarray structure, array creation functions, indexing, universal functions (ufuncs), and some shape manipulation routines. Good performance can be expected in JavaScript by using TypedArrays: these structures represent data in contiguous segments of memory. The JIT compilers of modern browsers should be smart enough to compile regular loops on these arrays quite efficiently.

Although only a small subset of NumPy would be sufficient, this approach does represent quite some work. There is no fundamental technological challenge behind this: it just requires some painful and slightly boring work. Yet, I think there can be some interest in having a lightweight "numpy.js" JavaScript library.

The other approach is radically different and much more sophisticated. Start from a Python function operating on NumPy arrays. Compile it to LLVM, and compile the LLVM code to JavaScript. The road from Python/NumPy to LLVM already exists: it's called **Numba**. As for the one from LLVM to JavaScript, it also exists: it's called **emscripten**. In theory, it should be possible to connect the LLVM output of Numba to the LLVM input of emscripten. That sounds easy, right?

Not so fast. A while ago, [I had asked the Numba developers about the feasibility of this approach](https://groups.google.com/a/continuum.io/d/msg/numba-users/ELAzQPFl6Ec/dbq6eQK134sJ). A major problem was that JIT-compiled Python functions with Numba used CPython under the hood. So some of CPython would have had to be compiled to JavaScript as well. That sounded overly complicated, especially when it comes to small, self-contained Python functions operating exclusively on NumPy arrays. So I let it go.

Recently, I heard about a new release of Numba, and I had another look. I discovered the `nopython` mode, which appeared to have been around for some time already. This mode sounds like something interesting for our purposes: if Python functions are compiled to LLVM without relying on CPython at all, maybe they can be successfully compiled to JavaScript?

A few days ago, I decided to have a go.


## What is LLVM?





## Getting the LLVM IR of a Python function with Numba



## Compiling the LLVM IR to JavaScript with emscripten

scalar


## Now with NumPy arrays

bugs and fix for rust


## Fixing the bugs with NumPy arrays


## Performance


## Limitations



## Conclusion


