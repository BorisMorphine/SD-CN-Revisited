import os
import launch

# Modern replacements
from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")

def get_installed_version(dist_name: str) -> str | None:
    try:
        return version(dist_name)
    except PackageNotFoundError:
        return None

with open(req_file, encoding="utf-8") as file:
    for raw_line in file:
        line = raw_line.strip()

        # Skip blanks, comments, and pip directives (e.g., -r, --find-links, hashes)
        if not line or line.startswith("#") or line.startswith(("-", "--")):
            continue

        try:
            req = Requirement(line)  # robust parser (handles extras, markers, specifiers)
            # Respect environment markers like ; python_version<"3.11"
            if req.marker and not req.marker.evaluate():
                continue

            dist_name = req.name  # distribution name (no extras)
            installed = get_installed_version(dist_name)

            # If no specifier (just a name), mimic original behavior:
            if not req.specifier:
                if not installed or not launch.is_installed(dist_name):
                    launch.run_pip(
                        f"install {line}",
                        f"SD-CN-Animation requirement: {line}"
                    )
                continue

            # There is at least one version specifier (==, >=, ~=, etc.)
            spec: SpecifierSet = req.specifier
            if not installed or (installed and not spec.contains(installed, prereleases=True)):
                # Install exactly what's written on the line (keeps extras/markers)
                launch.run_pip(
                    f"install {line}",
                    f"SD-CN-Animation requirement: enforcing {line} (was {installed or 'not installed'})"
                )

        except Exception as e:
            print(e)
            print(f"Warning: Failed to process requirement line: {raw_line.rstrip()}")
