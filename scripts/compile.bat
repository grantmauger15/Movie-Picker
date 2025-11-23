@echo off
echo Cleaning old build files...
rmdir /s /q build dist 2>nul
del /q movie.spec 2>nul
del /q movie.exe 2>nul

echo.
echo Building movie.exe...
echo.

pyinstaller --onefile movie.py

echo.
echo Moving movie.exe to root directory...
move dist\movie.exe movie.exe

echo.
echo Cleaning up build folders...
rmdir /s /q build dist
del /q movie.spec

echo.
echo Build complete! movie.exe is ready in the root folder.
echo.
pause
```

**What it does:**
1. Cleans up old builds
2. Builds the `.exe` (creates it in `dist` folder)
3. Moves `movie.exe` from `dist` to your root directory
4. Deletes the `build`, `dist`, and `movie.spec` files to keep things clean

**Your folder structure after running:**
```
cli/
├── movie.py
├── movies.csv
├── movie.exe          ← Your executable is here!
└── build.bat