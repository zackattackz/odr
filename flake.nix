{
  description = "Flake providing odoo-container-runner package and dev shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = nixpkgs.lib.platforms.unix;
      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system: f { pkgs = import nixpkgs { inherit system; }; } system
        );
      outputPackages = forEachSupportedSystem (
        { pkgs }:
        _: with pkgs.python3Packages; {
          python3Packages.odoo-container-runner = buildPythonPackage {
            pname = "odr";
            version = "0.1.0";
            pyproject = true;
            src = ./.;
            build-system = [ setuptools ];
            pythonImportsCheck = [ "odr" ];
            nativeBuildInputs = [ setuptools ];
          };
        }
      );
    in
    {
      packages = outputPackages;
      devShells = forEachSupportedSystem (
        { pkgs }:
        system: {
          default = pkgs.mkShell {
            packages = with pkgs; [
              nixfmt-rfc-style
              python3
              python3Packages.black
              python3Packages.pip-tools
              python3Packages.twine
              # outputPackages.${system}.python3Packages.odoo-container-runner
            ];
            buildInputs = [ pkgs.bashInteractive ];
          };
        }
      );
    };
}
