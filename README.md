# Basic script for supporting Ubuntu servers using Fabric

## Commands available
- other commands:
  - `apt_installed` - get installed packages list
  - `bootstrap` - provisioning for clean Ubuntu VM
  - `needs_reboot` - checks whether the OS needs reboot
  - `os_reboot` - restart
  - `os_update` - upgrade packages
  - `ps_os`
  - `pstree`
  - `uname`
  - `uptime`

## Provisioning

### Usage
`fab -H ${host} bootstrap:${password_root},${password}` to provision a VM

### Provisioning steps done
- creates remote user with the same name as local one (sufficient for me so far)
- adds user to sudoers
- places local user public SSH key to remote to allow password-less login
- upgrades packages
- enables firewall opening ports `22`, `10022`, `80` and `443`
- disables password authentication
- disables SSH root login
- installs packages, mainly a number of handy tools plus `docker`

