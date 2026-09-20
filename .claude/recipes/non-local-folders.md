# Folders that are not local

All four actions work on whatever the operating system presents as a path, so a folder is
supported exactly as far as it is mounted: a cloud drive's sync folder (pCloud, Google
Drive, Dropbox, rclone), a mounted share or a mapped drive letter, `/mnt/c` under WSL, a
VirtualBox or VMware share. There is no protocol code and no cloud API anywhere — adding
one would be a new repository, and the sync folder already covers the case.

Three things follow from that, and each is load bearing:

- **A folder can be typed, not only browsed.** The platform dialog only shows what it
  already knows about, which leaves out a UNC share, a path under `\\wsl$`, and any mount
  point it will not descend into. `SMSFolderList` therefore has a field beside its browse
  button, and nothing typed into it is checked against the disk: a share that is offline
  right now is still the folder the user means.
- **A folder that did not answer is never reported as an empty one.** See [domain-layer.md](domain-layer.md):
  `CheckFolder` runs before every walk, and `FileSystemRepository.probe_folder`
  gives the stat a deadline because a dead mount blocks rather than failing.
- **Every action runs in a worker, with a Cancel button.** See
  [application-layer.md](application-layer.md). A scan over a share is minutes, and Tk stops painting for all of it
  otherwise.

Two gaps are known and deliberate. A share that is unmounted but whose mount point still
exists locally reads as a readable empty folder, which no probe can tell apart without
reading the mount table. And a duplicate scan still compares every pair of files by
reading both whole, which is the expensive thing to do over a network; grouping by size
and digest first is the fix, and it is not done yet.
