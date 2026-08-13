@echo off
setlocal enabledelayedexpansion

rem ---------------------------------------------------------------------------
rem  mirror.bat - the backup of record for the Corpus repo, and an observable one.
rem
rem  Three legs, each checked separately:
rem    1. robocopy  C:\CORPUS -> Dropbox\Corpus-mirror  (working tree, no .git)
rem    2. git bundle --all    -> Dropbox\Corpus-mirror  (whole history, one file)
rem    3. FreeFileSync Repo-mirrors -> D:\CORPUS         (full copy incl. .git)
rem
rem  Corpus moved out of Dropbox 2026-08-13, so the working tree no longer races
rem  the sync. This puts a copy back into Dropbox (legs 1+2) and onto D: (leg 3),
rem  the same shape OSINT's mirror uses.
rem
rem  .workroot is a transient, gitignored folder of symlinks into OSINT that
rem  scripts\rebuild.py creates; /XD keeps it out of the mirror, /XJ stops
rem  robocopy following any junction or symlinked dir into a second copy.
rem
rem  Every run appends ONE dated line to logs\mirror_log.md saying ok or FAIL and
rem  carrying all three exit codes.
rem
rem  ASCII only, deliberately: cmd reads a .bat in the OEM codepage, so a UTF-8
rem  em-dash in an echoed line reaches the log as mojibake.
rem
rem  Exit code: 0 if all three legs passed, 1 otherwise.
rem ---------------------------------------------------------------------------

set "REPO=C:\CORPUS"
set "DROPBOX=C:\Users\bill\Dropbox\Corpus-mirror"
set "LOG=%REPO%\logs\mirror_log.md"
set "STATUS=ok"

for /f "delims=" %%t in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyy-MM-dd HH:mm')"') do set "TS=%%t"

rem --- leg 1: working tree to Dropbox -----------------------------------------
rem  robocopy returns a BIT FIELD, not a status: 0-7 are all success (1=copied,
rem  2=extras, 4=mismatched...). Only >=8 is a real failure. Testing `errorlevel 1`
rem  here would report FAIL on every run that copied a single file.
robocopy "%REPO%" "%DROPBOX%" /MIR /XD .git .workroot /XJ /NFL /NDL /NP
set "RC=!ERRORLEVEL!"
if !RC! GEQ 8 set "STATUS=FAIL"

rem --- leg 2: full history as a bundle ----------------------------------------
git -C "%REPO%" bundle create "%DROPBOX%\corpus.bundle" --all
set "GB=!ERRORLEVEL!"
if not "!GB!"=="0" set "STATUS=FAIL"

rem --- leg 3: FreeFileSync to D: ----------------------------------------------
rem  Repo-mirrors.ffs_batch is maintained by Bill; carry Errors Ignore="false" so a
rem  genuine error reaches us here. FFS: 0 = success, non-zero = warnings, errors or
rem  cancellation. Its own per-run logs land in logs\mirror-ffs\.
"C:\Program Files\FreeFileSync\FreeFileSync.exe" "%~dp0Repo-mirrors.ffs_batch"
set "FF=!ERRORLEVEL!"
if not "!FF!"=="0" set "STATUS=FAIL"

rem --- one dated line, whatever happened --------------------------------------
if not exist "%REPO%\logs" mkdir "%REPO%\logs"
>>"%LOG%" echo - **!TS!** - !STATUS! - robocopy=!RC! bundle=!GB! ffs=!FF!

if "!STATUS!"=="FAIL" (
  echo.
  echo mirror.bat: FAILED - robocopy=!RC! bundle=!GB! ffs=!FF!
  echo   see %LOG% and logs\mirror-ffs\
  endlocal & exit /b 1
)

echo mirror.bat: ok - robocopy=!RC! bundle=!GB! ffs=!FF!
endlocal & exit /b 0
