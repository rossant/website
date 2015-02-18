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
>>> import os
>>> import numpy as np
>>> import llvmlite.binding as ll
>>> import llvmlite.ir as llvmir
>>> import numba
>>> from numba import jit
>>> from numba import int32
```

It seems there is an easy way to get the LLVM IR of a JIT'ed in the development version, but this version didn't work for me, so here is a custom function doing the same thing (we'll make extensive use of unstable API in this post so most things are likely to break with different versions of Numba and other libraries...):

```python
>>> def llvm(func, sig=None):
...     """Return the LLVM IR of a @jit'ed function."""
...     if sig is None:
...         sig = func.signatures[0]
...     return str(func._compileinfos[sig].library._final_module)
```

Let's define a trivial function operating on scalars:

```python
>>> def f(x, y):
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

For simplicity, we have specified the input and output types explicitely. Numba can compile several overloaded versions of the same function at runtime, depending on the types of the arguments.

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

Two LLVM functions are defined here (`define` instruction):

* `@__main__.f.int32.int32`
* `@wrapper.__main__.f.int32.int32`

In LLVM, the names of global variables and functions start with a `@`. Names can contain many non-alphanumerical characters, including dots `.` and quotes `"`. LLVM IR is a strongly-typed language. As we can see in the function definitions, the first function takes four parameters (`i32*`, `i8*`, `i32`, `i32`) and returns a `i32` value.

Let's try to reverse-engineer this. The return value of this LLVM value is a success/failure output value. The actual value returned by our Python function is set in the pointer passed as a first argument. I'm not quite clear about the purpose of the second `i8*` argument; it might be related to the CPython environment and it doesn't seem important for what we're doing here. The last two `i32` arguments are our actual arguments `x` and `y`.

The body of that function seems to do what we expect:

```%.15 = add i32 %arg.y, %arg.x
store i32 %.15, i32* %ret, align 4```

The `add` instructions adds our two input numbers and saves them in a local variable `%.15`. Then, the `store` instruction puts that value in the `%ret` pointer passed as input: that's the return value of the function.

The `@wrapper.__main__.f.int32.int32` function is more complicated and we won't detail it at all here. This function wraps the core LLVM function and exposes it to the Python interpreter. For example, our input numbers are actually Python objects. Some works needs to be done with the Python C API to extract the actual numbers from these objects and pass them to the core LLVM function.

Since our ultimate goal is to compile `f()` in JavaScript where there's no such thing as a CPython interpreter, we only need the `@__main__.f.int32.int32` function here.

Now, let's try to compile this to JavaScript with emscripten!

## Compiling the LLVM IR to JavaScript with emscripten

Emscripten is an impressive piece of software. It can compile C/C++ code, even large projects like game engines ([Unreal Engine](https://blog.mozilla.org/blog/2014/03/12/mozilla-and-epic-preview-unreal-engine-4-running-in-firefox/) for example), to JavaScript. Emscripten uses Clang to compile C/C++ to LLVM, and a custom LLVM backend named *Fastcomp* to compile LLVM IR to JavaScript/**asm.js** (*an extraordinarily optimizable, low-level subset of JavaScript* [according to the project page](http://asmjs.org/)).

Let's get started. I first tried to use the easy SDK installer, but I had some issues and I had to compile emscripten from source (note: I'm using Ubuntu 14.04 64-bit). Instructions are [here](http://kripken.github.io/emscripten-site/docs/building_from_source/building_emscripten_from_source_on_linux.html#building-emscripten-on-linux). Also, I ended up using the `merge-3.5/merge-pnacl-3.5` branches of emscripten and fastcomp, but using `master` may work as well. The point was to ensure the same version of LLVM is used in Numba and emscripten, to avoid compatibility issues. After all, we're trying to fit a square peg in a round hole.

Fastcomp appears to share code with PNaCl, a project by Google that brings native applications to the Chrome browser through a sandboxing technology based on LLVM.

Here is a little function returning the LLVM library of a Python JIT'ed function. We'll use it later.

```python
>>> def get_lib(func, sig_index=0):
...     sig = func.signatures[sig_index]
...     compiled = func._compileinfos[sig]
...     lib = compiled.library
...     return lib
```

Now, we save the LLVM IR code to a `.ll` file, and we call `emcc` (the emscripten compiler) on this file with a JavaScript output:

```python
>>> os.chdir('/data/git/numpy-js')
>>> lib = get_lib(f)
>>> with open('scalar.ll', 'w') as fh:
...     fh.write((str(lib._final_module)))
>>> os.system('./emscripten/emcc scalar.ll -o scalar.js -O3 -s NO_EXIT_RUNTIME=1')
0
```

```python
>>> os.path.getsize('scalar.js')
138022
```

```python
>>> !cut -c-80 scalar.js | head -n5
var Module;if(!Module)Module=(typeof Module!=="undefined"?Module:null)||{};var m
var asm=(function(global,env,buffer) {
"use asm";var a=new global.Int8Array(buffer);var b=new global.Int16Array(buffer)
// EMSCRIPTEN_START_FUNCS
function ma(a){a=a|0;var b=0;b=i;i=i+a|0;i=i+15&-16;return b|0}function na(){ret
```

We now have a JavaScript file that supposedly implements our function. How do we call it from JavaScript? After all, what we have here is a sort of function compiled for a virtual machine in JavaScript. With Numba, we had a LLVM wrapper for Python that let us call the function from Python. Here, we have nothing, and we need to write our own wrapper.

I encountered a few difficulties:

* Programs compiled with emscripten are generally regular C programs with a main loop. However, what I want is an interactive access to my LLVM function from JavaScript.
* According to the documentation of emscripten, there is a way to access the LLVM functions from JavaScript. However, I must have done something wrong because I only managed to access the `main` entry point function (which actually doesn't exist).
* So I ended up creating a `main()` function in LLVM wrapping ` @__main__.f.int32.int32()`.

There are surely better ways to do it, but here is a little Python function adding this wrapper:

```python
>>> def add_wrapper(lib):
...     """Add a main entry point calling the function."""
...     main = """
...     define i32 @main(i64* %arg0, i8* %arg1, i32 %arg2, i32 %arg3)
...     {
...         %out = call i32 @__main__.add.int32.int32(i64* %arg0, i8* %arg1, i32 %arg2, i32 %arg3)
...         ret i32 %out
...     }
...     declare i32 @__main__.add.int32.int32(i64*, i8*, i32, i32)
...     """
...     ll_module = ll.parse_assembly(main)
...     ll_module.verify()
...     try:
...         lib.add_llvm_module(ll_module)
...     except RuntimeError:
...         print("Warning: the module as already been added.")
...     return lib
```

It's a bit ugly because the wrapper is hard-coded with the function's signature.

Once we have this `main()` function, we finally get access to it from JavaScript. But we're not done yet, because we need a way to retrieve the result. Recall that the result is stored via a pointer passed as a first argument to our LLVM function.

After a bit of googling, I ended up with a quick-and-dirty JavaScript wrapper:

```javascript
function Buffer(data) {
    // see http://kapadia.github.io/emscripten/2013/09/13/emscripten-pointers-and-pointers.html
    // data must be a TypedArray.
    this._typed_array = data;
    // Get data byte size, allocate memory on Emscripten heap, and get pointer
    var nDataBytes = data.length * data.BYTES_PER_ELEMENT;
    var dataPtr = Module._malloc(nDataBytes);
    // Copy data to Emscripten heap (directly accessed from Module.HEAPU8)
    var dataHeap = new Uint8Array(Module.HEAPU8.buffer, dataPtr, nDataBytes);
    dataHeap.set(new Uint8Array(data.buffer));
    this._data_heap = dataHeap;
    this.pointer = dataHeap.byteOffset;
}
Buffer.prototype.get = function () {
    return new this._typed_array.constructor(this._data_heap.buffer,
                                             this._data_heap.byteOffset,
                                             this._typed_array.length);
}
Buffer.prototype.free = function () {
    Module._free(this._data_heap.byteOffset);
}
function is_array(tp) {
    return (tp.indexOf(':') > -1);
}
function wrap(args) {
    // return pointer, env
    var arg_types = ['number', 'number'];
    // one number per argument
    for (var i = 0; i < args.length; i++) {
        arg_types.push('number');
    }
    var func_name = 'main';
    var func = Module.cwrap(func_name, 'number', arg_types);
    var wrapped = function(return_arr) {
        // Wrap TypedArrays into emscripten buffers.
        // Buffer with the return buffer, initialized with an array
        // passed as argument.
        var buffer_out = new Buffer(return_arr);
        // Wrap function arguments.
        var func_args = [buffer_out.pointer, 0];
        // Skip the first argument which is the return array.
        for (var i = 1; i < arguments.length; i++) {
            var arg;
            // Define the argument to send to the wrapped function.
            if (is_array(args[i-1])) {
                // If that argument is an array, pass the pointer to
                // an emscripten buffer containing the data.
                arg = new Buffer(arguments[i]).pointer;
            }
            else {
                // Otherwise, just pass the argument directly.
                arg = arguments[i];
            }
            func_args.push(arg);
        }
        func.apply(undefined, func_args);
        var result = buffer_out.get();
        return result;
    };
    return wrapped;
}
```

This wrapper connects JavaScript TypedArray buffers to the virtual machine buffers and pointers. We finally get a chance to call our compiled LLVM functions from JavaScript. Here is an interactive example:

```javascript
// We get the input numbers.
var arg1 = parseInt($('#my_arg1').val());
var arg2 = parseInt($('#my_arg2').val());
// We wrap the LLVM main() function, specifying the signature.
var add = wrap(['int', 'int']);
// We create a buffer that will contain the result.
var result = new Int32Array([0]);
result = add(result, arg1, arg2);
// We display the result.
$('#my_output').val(result[0]);
```

TODO: HTML calculator

## Now with NumPy arrays

bugs and fix for rust

## Fixing the bugs with NumPy arrays

## Performance

## Limitations

## Conclusion
