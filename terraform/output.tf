output "vm_ip" {
  value = opennebula_virtual_machine.todo-vm.ip
}

resource "local_file" "ansible_inventory" {
  filename        = "../ansible/inventory"
  file_permission = "0644"
  content         = <<EOT
[servers]
${opennebula_virtual_machine.todo-vm.ip} ansible_ssh_retries=10 ansible_ssh_timeout=30

[servers:vars]
ansible_user = "root"
ansible_ssh_extra_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
EOT
}
