{
  description = "asyncio-loop-local storage, singletons and deferred __aexit__'s. Init that pool once and reuse it!";

  outputs = { self, nixpkgs, flake-utils }:
    let
      deps = pyPackages: with pyPackages; [
        # no dependencies
      ];
      tools = pkgs: pyPackages: (with pyPackages; [
        pytest pytestCheckHook pytest-asyncio
        coverage pytest-cov
        mypy pytest-mypy
      ] ++ [pkgs.ruff]);

      asyncio-loop-local-package = {pkgs, python3Packages}:
        python3Packages.buildPythonPackage {
          pname = "asyncio-loop-local";
          version = "0.0.1";
          src = ./.;
          format = "pyproject";
          propagatedBuildInputs = deps python3Packages;
          nativeBuildInputs = [ python3Packages.setuptools ];
          checkInputs = tools pkgs python3Packages;
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
            buildInputs = [(defaultPython3Packages.python.withPackages deps)];
            nativeBuildInputs = tools pkgs defaultPython3Packages;
            shellHook = ''
              export PYTHONASYNCIODEBUG=1 PYTHONWARNINGS=error
            '';
          };
          packages.asyncio-loop-local = asyncio-loop-local;
          packages.default = asyncio-loop-local;
        }
    ) // { overlays.default = overlay; };
}
