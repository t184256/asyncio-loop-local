{
  description = "asyncio-loop-local storage, singletons and deferred __aexit__'s. Init that pool once and reuse it!";

  outputs = { self, nixpkgs, flake-utils }:
    let
      pyDeps = pyPackages: with pyPackages; [
        # no dependencies
      ];
      pyTestDeps = pyPackages: with pyPackages; [
        pytest pytestCheckHook pytest-asyncio
        coverage pytest-cov
      ];
      pyTools = pyPackages: with pyPackages; [ mypy ];

      tools = pkgs: with pkgs; [
        pre-commit
        ruff
        codespell
        actionlint
        python3Packages.pre-commit-hooks
      ];

      asyncio-loop-local-package = {pkgs, python3Packages}:
        python3Packages.buildPythonPackage {
          pname = "asyncio-loop-local";
          version = "0.0.1";
          src = ./.;
          disabled = python3Packages.pythonOlder "3.11";
          format = "pyproject";
          build-system = [ python3Packages.setuptools ];
          propagatedBuildInputs = pyDeps python3Packages;
          checkInputs = pyTestDeps python3Packages;
        };

      overlay = final: prev: {
        pythonPackagesExtensions =
          prev.pythonPackagesExtensions ++ [(pyFinal: pyPrev: {
            asyncio-loop-local = final.callPackage asyncio-loop-local-package {
              python3Packages = pyFinal;
            };
          })];
      };
    in
      flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs { inherit system; overlays = [ overlay ]; };
          defaultPython3Packages = pkgs.python311Packages;  # force 3.11

          asyncio-loop-local = pkgs.callPackage asyncio-loop-local-package {
            python3Packages = defaultPython3Packages;
          };
        in
        {
          devShells.default = pkgs.mkShell {
            buildInputs = [(defaultPython3Packages.python.withPackages (
              pyPkgs: pyDeps pyPkgs ++ pyTestDeps pyPkgs ++ pyTools pyPkgs
            ))];
            nativeBuildInputs = [(pkgs.buildEnv {
              name = "asyncio-loop-local-tools-env";
              pathsToLink = [ "/bin" ];
              paths = tools pkgs;
            })];
            shellHook = ''
              [ -e .git/hooks/pre-commit ] || \
                echo "suggestion: pre-commit install --install-hooks" >&2
              export PYTHONASYNCIODEBUG=1 PYTHONWARNINGS=error
            '';
          };
          packages.asyncio-loop-local = asyncio-loop-local;
          packages.default = asyncio-loop-local;
        }
    ) // { overlays.default = overlay; };
}
