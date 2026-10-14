# Third-party notices

## GitHub Spec Kit

This repository includes files from [GitHub Spec Kit](https://github.com/github/spec-kit) (version 0.16.2.dev0), used under the MIT License. Some of them may have been adapted for this project.

- `.claude/skills/speckit-*/`
- `.specify/`, except `.specify/memory/constitution.md` (this project's own constitution)

```text
MIT License

Copyright GitHub, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Qt for Python (PySide6)

The app is built on [PySide6](https://doc.qt.io/qtforpython/), which is installed as a dependency and is not included in this repository. PySide6 is available under the GNU LGPL v3. An `.app` bundle you build with py2app or PyInstaller contains the PySide6 and Qt libraries, so if you redistribute that bundle, the LGPL's terms for those libraries apply to it.
