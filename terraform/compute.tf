data "opennebula_template" "vm_template" {
  id = var.template_id  
}

data "opennebula_image" "template_disk_image" {
  id = data.opennebula_template.vm_template.disk[0].image_id
}

resource "opennebula_virtual_machine" "todo-vm" {

  name        = "todo-main-machine"
  description = "VM for the to-do app"
  template_id = var.template_id
  cpu         = 2
  vcpu        = 4
  memory      = 2048
  group       = var.op_group
  permissions = "660"

  disk {
    image_id = data.opennebula_image.template_disk_image.id
    size     = 20480
  }

  context = {
    NETWORK        = "YES"
    SSH_PUBLIC_KEY = "$USER[SSH_PUBLIC_KEY]"
    START_SCRIPT   = "apt update && apt upgrade -y"
  }

  tags = {
    environment = var.environment
  }
}
