Title: NumPy in the browser: proof of concept with Numba, LLVM, and emscripten
Tags: python

It's been a while since I wanted to try to bring some of NumPy to the browser. I've already discussed the motivations for this [in a previous post last year]({filename}2014-03-31-scientific-python-in-the-browser-its-coming.md). One of the main motivations as far as I'm concerned is to enable interactive visualizations in offline notebooks (including nbviewer). In this post, I'll describe a proof of concept where I successfully compile NumPy-aware Python functions to JavaScript using Numba, LLVM, and emscripten.

<!-- PELICAN_END_SUMMARY -->

How to bring NumPy to the browser? There are at least two quite different approaches.

The first approach consists of reimplementing a tiny subset of NumPy in JavaScript. Many computations can be implemented with a minimum feature set of NumPy: the ndarray structure, array creation functions, indexing, universal functions (ufuncs), and some shape manipulation routines. Good performance can be expected in JavaScript by using TypedArrays: these structures represent data in contiguous segments of memory. The JIT compilers of modern browsers should be smart enough to compile regular loops on these arrays quite efficiently.

Although only a small subset of NumPy would be sufficient, this approach does represent quite some work. There is no fundamental technological challenge behind this: it just requires some painful and slightly boring work. Yet, I think there can be some interest in having a lightweight "numpy.js" JavaScript library.

The other approach is radically different and much more sophisticated. Start from a Python function operating on NumPy arrays. Compile it to LLVM, and compile the LLVM code to JavaScript. The road from Python/NumPy to LLVM already exists: it's called **Numba**. As for the one from LLVM to JavaScript, it also exists: it's called **emscripten**. In theory, it should be possible to connect the LLVM output of Numba to the LLVM input of emscripten. That sounds easy, right?

Not so fast. A while ago, [I had asked the Numba developers about the feasibility of this approach](https://groups.google.com/a/continuum.io/d/msg/numba-users/ELAzQPFl6Ec/dbq6eQK134sJ). A major problem was that Python functions that are JIT-compiled with Numba use CPython under the hood. So some of CPython would have to be compiled to JavaScript as well. That sounded overly complicated, especially when it comes to small, self-contained Python functions operating exclusively on NumPy arrays. So I let it go.

Recently, I heard about a new release of Numba, and I had another look. I discovered the `nopython` mode, which appeared to have been around for some time already. This mode sounds like something interesting for our purposes: if Python functions are compiled to LLVM without relying on CPython at all, maybe they can be successfully compiled to JavaScript?

Since I had long wanted to play with LLVM, I decided to have a go.

## What is LLVM?

But first, what is LLVM exactly? It is a modular compiler architecture. The core of LLVM is a machine-independent assembly-like language called the **LLVM Intermediate Representation** (IR). Think of it as a strongly-typed instruction set for a virtual machine (even if *the scope of the project is not limited to the creation of virtual machines*, [tells us Wikipedia](http://en.wikipedia.org/wiki/LLVM)).

The IR abstracts away details of the compilation target. As such, it is common target for various language frontends (C, C++, Haskell, Python, and many others) and microarchitecture backends (x86, ARM, Nvidia PTX which is used in CUDA-enabled GPUs, etc.). LLVM also comes with a powerful and modular architecture for optimization passes.

LLVM seems to be quite popular these days, with a strong industrial support, notably by Apple. For example, Apple's **Clang** is a LLVM-based C/C++/Objective C compiler that aims at replacing GCC's compilers for these languages. The compilers of modern languages like Julia and Rust are also built with LLVM.

## What is Numba?

Now, the idea of Numba is the following. Take a Python function performing numerical operations on NumPy arrays. Normally, this function is interpreted by CPython. It performs Python and NumPy C API calls to execute these operations efficiently.

With Numba, things happen quite differently. At runtime, the function bytecode is analyzed, types are inferred, and LLVM IR is generated before being compiled to machine code. In *nopython mode*, the LLVM IR doesn't make Python C API calls. There are many situations where the Python function cannot be compiled in nopython mode because it uses non-trivial Python features or data structures. In this case, the *object mode* is activated and the LLVM IR makes many Python C API calls.

That's it for the theory. Now let's get our hands dirty.

## Getting the LLVM IR of a Python function with Numba

Let's first import Numba (I installed the latest stable release with conda):

```python
>>> import numpy as np
>>> import llvmlite.binding as ll
>>> import llvmlite.ir as llvmir
>>> import numba
>>> from numba import jit
>>> from numba import int32
```

It seems there is an easy way to get the LLVM IR of a JIT'ed in the development version, but this version didn't work for me, so here is a custom function doing the same thing:

```python
>>> def llvm(func, sig=None):
...     """Return the LLVM IR of a @jit'ed function."""
...     if sig is None:
...         sig = func.signatures[0]
...     return str(func._compileinfos[sig].library._final_module)
```

Let's define a trivial function operating on scalars:

```python
>>> @jit(int32(int32, int32), nopython=True)
... def f(x, y):
...     return x + y
```

```python
>>> f(1, 2)
3
```

Now, let's compile it in nopython mode:

```python
>>> @jit(int32(int32, int32), nopython=True)
... def f(x, y):
...     return x + y
```

Let's have a look at the generated LLVM IR:

```python
>>> print(llvm(f))
[...]

; Function Attrs: nounwind
define i32 @__main__.f.int32.int32(i32* nocapture %ret, i8* nocapture readnone %env, i32 %arg.x, i32 %arg.y) #0 {
entry:
  %.15 = add i32 %arg.y, %arg.x
  store i32 %.15, i32* %ret, align 4
  ret i32 0
}

[...]

define i8* @wrapper.__main__.f.int32.int32(i8* nocapture readnone %py_closure, i8* %py_args, i8* %py_kws) {
entry:
  %.4 = alloca i8*, align 8
  %.5 = alloca i8*, align 8
  %.6 = call i32 (i8*, i8*, i8*, i8**, ...)* @PyArg_ParseTupleAndKeywords(i8* %py_args, i8* %py_kws, i8* getelementptr inbounds ([3 x i8]* @.const.OO, i64 0, i64 0), i8** getelementptr inbounds ([3 x i8*]* @.kwlist, i64 0, i64 0), i8** %.4, i8** %.5)
  %.7 = icmp eq i32 %.6, 0
  br i1 %.7, label %entry.if, label %entry.endif, !prof !0

entry.if:                                         ; preds = %entry.endif1.1.endif, %entry.endif1.1, %entry.endif, %entry
  %merge = phi i8* [ null, %entry.endif1.1 ], [ null, %entry.endif ], [ null, %entry ], [ %.57, %entry.endif1.1.endif ]
  ret i8* %merge

entry.endif:                                      ; preds = %entry
  %.11 = load i8** %.4, align 8
  %.12 = call i8* @PyNumber_Long(i8* %.11)
  %.13 = call i64 @PyLong_AsLongLong(i8* %.12)
  call void @Py_DecRef(i8* %.12)
  %.16 = call i8* @PyErr_Occurred()
  %.17 = icmp eq i8* %.16, null
  br i1 %.17, label %entry.endif1.1, label %entry.if, !prof !1

entry.endif1.1:                                   ; preds = %entry.endif
  %.21 = load i8** %.5, align 8
  %.22 = call i8* @PyNumber_Long(i8* %.21)
  %.23 = call i64 @PyLong_AsLongLong(i8* %.22)
  call void @Py_DecRef(i8* %.22)
  %.26 = call i8* @PyErr_Occurred()
  %.27 = icmp eq i8* %.26, null
  br i1 %.27, label %entry.endif1.1.endif, label %entry.if, !prof !1

entry.endif1.1.endif:                             ; preds = %entry.endif1.1
  %.15.i = add i64 %.23, %.13
  %sext = shl i64 %.15.i, 32
  %.51 = ashr exact i64 %sext, 32
  %.57 = call i8* @PyInt_FromLong(i64 %.51)
  br label %entry.if
}
```

That's a lot of code for such a simple function! And yet I have only kept the most relevant bits.

Two LLVM functions are defined here (`define` instruction)

## Compiling the LLVM IR to JavaScript with emscripten

scalar

## Now with NumPy arrays

bugs and fix for rust

## Fixing the bugs with NumPy arrays

## Performance

## Limitations

## Conclusion
