from pip._internal.operations import freeze

with open("requirements.txt", "w") as req_file:
    req_file.write('\n'.join(freeze.freeze()))
