@echo off
for %%F in (*.webp) do (
    dwebp "%%F" -o "%%~nF.png"
    del "%%F"
)