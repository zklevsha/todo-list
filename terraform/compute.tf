resource "opennebula_virtual_machine" "todo-vm" {

  name        = "todo-main-machine"
  description = "VM for the to-do app"
  template_id = var.template_id
  cpu         = 2
  vcpu        = 4
  memory      = 2048
  group       = var.op_group
  permissions = "660"

  context = {
    NETWORK        = "YES"
    SSH_PUBLIC_KEY = "$USER[SSH_PUBLIC_KEY]"
    START_SCRIPT   = "apt update && apt upgrade -y"
  }

  tags = {
    environment = var.environment
  }
}
