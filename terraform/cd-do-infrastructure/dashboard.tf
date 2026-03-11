# --- DATADOG DASHBOARD (CD-DO-INFRASTRUCTURE) ---
# Portfolio-ready SOC dashboard for CoreDirective infrastructure
# Created by Phase 07-02

resource "datadog_dashboard" "soc" {
  title       = "CoreDirective Security Operations Center"
  description = "Production monitoring for CoreDirective infrastructure on DigitalOcean"
  layout_type = "ordered"

  tags = ["team:coredirective"]

  # ===========================================================================
  # GROUP 1: INFRASTRUCTURE HEALTH
  # ===========================================================================

  widget {
    group_definition {
      title            = "Infrastructure Health"
      layout_type      = "ordered"
      background_color = "vivid_blue"

      # --- Host Map ---
      widget {
        hostmap_definition {
          title      = "Host Overview"
          title_size = "16"
          scope      = ["host:${local.dd_host}"]
          node_type  = "host"

          request {
            fill {
              q = "avg:system.cpu.user{host:${local.dd_host}} by {host}"
            }
          }

          style {
            palette      = "green_to_orange"
            palette_flip = false
          }
        }
      }

      # --- CPU Timeseries ---
      widget {
        timeseries_definition {
          title      = "CPU Usage"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "line"

            query {
              metric_query {
                name  = "cpu_user"
                query = "avg:system.cpu.user{host:${local.dd_host}}"
              }
            }

            query {
              metric_query {
                name  = "cpu_system"
                query = "avg:system.cpu.system{host:${local.dd_host}}"
              }
            }

            formula {
              formula_expression = "cpu_user + cpu_system"
              alias              = "Total CPU %"
            }

            style {
              palette = "dog_classic"
            }
          }

          yaxis {
            min = "0"
            max = "100"
          }
        }
      }

      # --- Memory Timeseries ---
      widget {
        timeseries_definition {
          title      = "Memory Usage"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "line"

            query {
              metric_query {
                name  = "mem_used"
                query = "avg:system.mem.used{host:${local.dd_host}}"
              }
            }

            query {
              metric_query {
                name  = "mem_total"
                query = "avg:system.mem.total{host:${local.dd_host}}"
              }
            }

            formula {
              formula_expression = "(mem_used / mem_total) * 100"
              alias              = "Memory %"
            }

            style {
              palette = "warm"
            }
          }

          yaxis {
            min = "0"
            max = "100"
          }
        }
      }

      # --- Disk Usage Query Value ---
      widget {
        query_value_definition {
          title      = "Disk Usage"
          title_size = "16"
          live_span  = "5m"
          autoscale  = false
          precision  = 1

          request {
            query {
              metric_query {
                name       = "disk"
                query      = "avg:system.disk.in_use{host:${local.dd_host},device:/dev/vda1} * 100"
                aggregator = "avg"
              }
            }

            formula {
              formula_expression = "disk"
            }

            conditional_formats {
              comparator = ">"
              value      = 80
              palette    = "white_on_red"
            }

            conditional_formats {
              comparator = ">="
              value      = 60
              palette    = "white_on_yellow"
            }

            conditional_formats {
              comparator = "<"
              value      = 60
              palette    = "white_on_green"
            }
          }

          custom_unit = "%"
        }
      }

      # --- Network I/O Timeseries ---
      widget {
        timeseries_definition {
          title      = "Network I/O"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "area"
            q            = "avg:system.net.bytes_sent{host:${local.dd_host}}"

            style {
              palette = "cool"
            }
          }

          request {
            display_type = "area"
            q            = "avg:system.net.bytes_rcvd{host:${local.dd_host}}"

            style {
              palette = "purple"
            }
          }
        }
      }
    }
  }

  # ===========================================================================
  # GROUP 2: CONTAINER FLEET
  # ===========================================================================

  widget {
    group_definition {
      title            = "Container Fleet"
      layout_type      = "ordered"
      background_color = "vivid_green"

      # --- Container Health Check Status ---
      widget {
        check_status_definition {
          title      = "Container Health"
          title_size = "16"
          live_span  = "1h"
          check      = "docker.container_health"
          grouping   = "cluster"
          group_by   = ["container_name"]
          tags       = ["host:${local.dd_host}"]
        }
      }

      # --- Container CPU by Name ---
      widget {
        timeseries_definition {
          title      = "Container CPU Usage"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "line"
            q            = "avg:docker.cpu.usage{host:${local.dd_host}} by {container_name}"

            style {
              palette = "dog_classic"
            }
          }
        }
      }

      # --- Container Memory by Name ---
      widget {
        timeseries_definition {
          title      = "Container Memory (RSS)"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "line"
            q            = "avg:docker.mem.rss{host:${local.dd_host}} by {container_name}"

            style {
              palette = "cool"
            }
          }
        }
      }

      # --- Running Container Count ---
      widget {
        query_value_definition {
          title      = "Running Containers"
          title_size = "16"
          live_span  = "5m"
          autoscale  = false
          precision  = 0

          request {
            query {
              metric_query {
                name       = "containers"
                query      = "avg:docker.containers.running{host:${local.dd_host}}"
                aggregator = "avg"
              }
            }

            formula {
              formula_expression = "containers"
            }

            conditional_formats {
              comparator = ">="
              value      = 5
              palette    = "white_on_green"
            }

            conditional_formats {
              comparator = "<"
              value      = 5
              palette    = "white_on_red"
            }
          }
        }
      }
    }
  }

  # ===========================================================================
  # GROUP 3: SECURITY OPERATIONS
  # ===========================================================================

  widget {
    group_definition {
      title            = "Security Operations"
      layout_type      = "ordered"
      background_color = "vivid_orange"

      # --- Falco Event Stream (populated after Plan 07-03) ---
      widget {
        event_stream_definition {
          title      = "Falco Runtime Alerts"
          title_size = "16"
          live_span  = "1w"
          query      = "source:falcosidekick"
          event_size = "s"
        }
      }

      # --- Failed SSH Attempts Query Value ---
      widget {
        query_value_definition {
          title      = "Failed SSH Attempts (24h)"
          title_size = "16"
          live_span  = "1d"
          autoscale  = false
          precision  = 0

          request {
            query {
              event_query {
                name        = "ssh_failures"
                data_source = "logs"
                indexes     = ["*"]

                search {
                  query = "source:auth service:sshd status:error host:${local.dd_host}"
                }

                compute {
                  aggregation = "count"
                }
              }
            }

            formula {
              formula_expression = "ssh_failures"
            }

            conditional_formats {
              comparator = ">"
              value      = 50
              palette    = "white_on_red"
            }

            conditional_formats {
              comparator = ">"
              value      = 10
              palette    = "white_on_yellow"
            }

            conditional_formats {
              comparator = "<="
              value      = 10
              palette    = "white_on_green"
            }
          }
        }
      }

      # --- Falco Events by Priority Timeseries (populated after Plan 07-03) ---
      widget {
        timeseries_definition {
          title      = "Falco Events by Priority (7d)"
          title_size = "16"
          live_span  = "1w"

          request {
            display_type = "bars"

            query {
              event_query {
                name        = "falco"
                data_source = "logs"
                indexes     = ["*"]

                search {
                  query = "source:falcosidekick"
                }

                compute {
                  aggregation = "count"
                }

                group_by {
                  facet = "priority"
                  limit = 10

                  sort {
                    aggregation = "count"
                    order       = "desc"
                  }
                }
              }
            }

            formula {
              formula_expression = "falco"
            }
          }
        }
      }

      # --- Auth Log Stream ---
      widget {
        log_stream_definition {
          title      = "SSH Auth Failures"
          title_size = "16"
          live_span  = "1d"
          query      = "source:auth service:sshd status:error host:${local.dd_host}"
          columns    = ["host", "service", "status", "message"]
        }
      }
    }
  }

  # ===========================================================================
  # GROUP 4: APPLICATION PERFORMANCE
  # ===========================================================================

  widget {
    group_definition {
      title            = "Application Performance"
      layout_type      = "ordered"
      background_color = "vivid_purple"

      # --- PostgreSQL Active Connections ---
      widget {
        query_value_definition {
          title      = "PostgreSQL Connections"
          title_size = "16"
          live_span  = "5m"
          autoscale  = false
          precision  = 0

          request {
            query {
              metric_query {
                name       = "pg_conns"
                query      = "avg:postgresql.connections{host:${local.dd_host}}"
                aggregator = "avg"
              }
            }

            formula {
              formula_expression = "pg_conns"
            }

            conditional_formats {
              comparator = ">"
              value      = 80
              palette    = "white_on_red"
            }

            conditional_formats {
              comparator = ">"
              value      = 50
              palette    = "white_on_yellow"
            }

            conditional_formats {
              comparator = "<="
              value      = 50
              palette    = "white_on_green"
            }
          }
        }
      }

      # --- n8n Container CPU Timeseries ---
      widget {
        timeseries_definition {
          title      = "n8n Container CPU (24h)"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "line"
            q            = "avg:docker.cpu.usage{container_name:cd-service-n8n,host:${local.dd_host}}"

            style {
              palette = "orange"
            }
          }
        }
      }

      # --- Error Log Count ---
      widget {
        query_value_definition {
          title      = "Error Logs (24h)"
          title_size = "16"
          live_span  = "1d"
          autoscale  = false
          precision  = 0

          request {
            query {
              event_query {
                name        = "errors"
                data_source = "logs"
                indexes     = ["*"]

                search {
                  query = "status:error host:${local.dd_host}"
                }

                compute {
                  aggregation = "count"
                }
              }
            }

            formula {
              formula_expression = "errors"
            }

            conditional_formats {
              comparator = ">"
              value      = 100
              palette    = "white_on_red"
            }

            conditional_formats {
              comparator = ">"
              value      = 20
              palette    = "white_on_yellow"
            }

            conditional_formats {
              comparator = "<="
              value      = 20
              palette    = "white_on_green"
            }
          }
        }
      }

      # --- Error Log Stream ---
      widget {
        log_stream_definition {
          title      = "Error Logs (All Containers)"
          title_size = "16"
          live_span  = "1d"
          query      = "status:error host:${local.dd_host}"
          columns    = ["host", "service", "status", "message"]
        }
      }
    }
  }

  # ===========================================================================
  # GROUP 5: COMPLIANCE POSTURE
  # ===========================================================================

  widget {
    group_definition {
      title            = "Compliance Posture"
      layout_type      = "ordered"
      background_color = "vivid_yellow"

      # --- CIS Docker Bench PASS Count ---
      widget {
        query_value_definition {
          title      = "CIS Checks Passing"
          title_size = "16"
          live_span  = "1w"
          autoscale  = false
          precision  = 0

          request {
            query {
              metric_query {
                name       = "cis_pass"
                query      = "avg:cis.docker_bench.pass{host:${local.dd_host}}"
                aggregator = "last"
              }
            }

            formula {
              formula_expression = "cis_pass"
            }

            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_green"
            }
          }
        }
      }

      # --- CIS Docker Bench WARN Count ---
      widget {
        query_value_definition {
          title      = "CIS Findings Open"
          title_size = "16"
          live_span  = "1w"
          autoscale  = false
          precision  = 0

          request {
            query {
              metric_query {
                name       = "cis_warn"
                query      = "avg:cis.docker_bench.warn{host:${local.dd_host}}"
                aggregator = "last"
              }
            }

            formula {
              formula_expression = "cis_warn"
            }

            conditional_formats {
              comparator = ">"
              value      = 10
              palette    = "white_on_red"
            }

            conditional_formats {
              comparator = ">"
              value      = 0
              palette    = "white_on_yellow"
            }

            conditional_formats {
              comparator = "<="
              value      = 0
              palette    = "white_on_green"
            }
          }
        }
      }

      # --- CIS Docker Bench INFO Count ---
      widget {
        query_value_definition {
          title      = "CIS Info Items"
          title_size = "16"
          live_span  = "1w"
          autoscale  = false
          precision  = 0

          request {
            query {
              metric_query {
                name       = "cis_info"
                query      = "avg:cis.docker_bench.info{host:${local.dd_host}}"
                aggregator = "last"
              }
            }

            formula {
              formula_expression = "cis_info"
            }
          }
        }
      }

      # --- Compliance Trend Timeseries (90 days) ---
      widget {
        timeseries_definition {
          title      = "CIS Compliance Trend (90d)"
          title_size = "16"
          live_span  = "3mo"

          request {
            display_type = "line"
            q            = "avg:cis.docker_bench.pass{host:${local.dd_host}}"

            style {
              palette = "green"
            }
          }

          request {
            display_type = "line"
            q            = "avg:cis.docker_bench.warn{host:${local.dd_host}}"

            style {
              palette = "orange"
            }
          }

          request {
            display_type = "line"
            q            = "avg:cis.docker_bench.info{host:${local.dd_host}}"

            style {
              palette = "grey"
            }
          }
        }
      }

      # --- Compliance Note ---
      widget {
        note_definition {
          content          = "Falco runtime detection active (Plan 07-03) | Audit logs shipped to DO Spaces every 6h (Plan 07-05) | CIS Docker Bench scans weekly (Plan 07-04)"
          background_color = "gray"
          font_size        = "14"
          text_align       = "center"
          show_tick        = false
          has_padding      = true
        }
      }
    }
  }
}

# --- DASHBOARD URL OUTPUT ---

output "datadog_dashboard_url" {
  description = "URL to the CoreDirective SOC dashboard in Datadog"
  value       = datadog_dashboard.soc.url
}
