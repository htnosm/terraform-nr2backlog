output "newrelic_account_id" {
  value = var.newrelic_account_id
}

output "event_bus_name" {
  value = one([for x in newrelic_notification_channel.event_bridge.property : x.value if x.key == "eventSource"])
}
