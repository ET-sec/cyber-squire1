# --- AGENT ACTIVITY DASHBOARD (CoSAI Visibility, Phase 20 Plan 20-05) ---
#
# Per-agent_id breakdown of LLM-caller activity across the CoreDirective
# stack. 4 widgets, all faceted BY agent_id so the dashboard auto-discovers
# new agents from incoming telemetry (registry-driven, not dashboard-driven).
#
# Maps to Phase 20 Success Criterion 6. Authored alongside the host-level
# Datadog tag, n8n shared snippet, and Python ddtrace helpers in this plan.
#
# NOTE on metric names:
# The query bodies below reference ddtrace canonical metric names
# (trace.<service>.request.count, trace.http.request.count,
# trace.tool.invocation.count). Real metric names depend on which Datadog
# integration the agent's runtime is wired against. If a widget shows no
# data after 24h of telemetry, swap the metric name in the query body for
# the actual one emitted by the agent's runtime (use the Datadog Metrics
# Explorer to confirm). The Top Tools widget specifically depends on a
# tool.invocation custom span emitted by a LangGraph wrapper that lands in
# Phase 21; expect that widget to stay empty until then.

resource "datadog_dashboard" "agent_activity" {
  title       = "Agent Activity (CoSAI Visibility)"
  description = "Per-agent_id breakdown of calls per minute, success rate, top destinations, and top tools. Authoritative source for which agents are doing what across the CoreDirective stack. Phase 20 limitation: cdirective_bot traffic appears under agent_id:openclaw due to host-level tag inheritance through the openclaw gateway; per-bot breakdown deferred to Phase 21."
  layout_type = "ordered"

  tags = ["team:coredirective", "phase:20", "framework:cosai"]

  # ===========================================================================
  # GROUP 1: VISIBILITY PHASE 1 OF 3 (CoSAI)
  # ===========================================================================
  # Foundation for contextual access control (Phase 21) and policy
  # enforcement (Phase 22). Known Phase 20 limitation: cdirective_bot and
  # openclaw appear as one row (per-bot breakdown in Phase 21).

  widget {
    group_definition {
      title            = "Visibility Phase 1 of 3 (CoSAI)"
      layout_type      = "ordered"
      background_color = "vivid_blue"

      # --- Calls per Minute by Agent ---
      widget {
        timeseries_definition {
          title      = "Calls per Minute by Agent"
          title_size = "16"
          live_span  = "1d"

          request {
            display_type = "line"
            # ddtrace canonical metric for Anthropic LLM calls; if Python agents
            # use a different LLM SDK the metric prefix may change.
            q = "sum:trace.anthropic.request.count{*} by {agent_id}.as_rate()"

            style {
              palette = "dog_classic"
            }
          }
        }
      }

      # --- Success Rate by Agent (7d) ---
      widget {
        query_value_definition {
          title      = "Success Rate by Agent (7d)"
          title_size = "16"
          live_span  = "1w"
          autoscale  = true
          precision  = 1

          request {
            query {
              metric_query {
                name       = "ok"
                query      = "sum:trace.anthropic.request.count{status:ok} by {agent_id}.as_count()"
                aggregator = "avg"
              }
            }

            query {
              metric_query {
                name       = "total"
                query      = "sum:trace.anthropic.request.count{*} by {agent_id}.as_count()"
                aggregator = "avg"
              }
            }

            formula {
              formula_expression = "(ok / total) * 100"
              alias              = "Success %"
            }

            conditional_formats {
              comparator = ">"
              value      = 95
              palette    = "white_on_green"
            }

            conditional_formats {
              comparator = ">="
              value      = 90
              palette    = "white_on_yellow"
            }

            conditional_formats {
              comparator = "<"
              value      = 90
              palette    = "white_on_red"
            }
          }

          custom_unit = "%"
        }
      }

      # --- Top Destinations by Agent ---
      widget {
        toplist_definition {
          title      = "Top Destinations by Agent"
          title_size = "16"
          live_span  = "1d"

          request {
            q = "top(sum:trace.http.request.count{*} by {agent_id,http.url}, 10, 'sum', 'desc')"
          }
        }
      }

      # --- Top Tools by Agent ---
      # NOTE: requires a tool.invocation custom span. Phase 20 ships the
      # tag plumbing; the LangGraph wrapper that emits the span is a
      # Phase 21 deliverable. Expect this widget to stay empty until then.
      widget {
        toplist_definition {
          title      = "Top Tools by Agent"
          title_size = "16"
          live_span  = "1d"

          request {
            q = "top(sum:trace.tool.invocation.count{*} by {agent_id,tool.name}, 10, 'sum', 'desc')"
          }
        }
      }

      # --- Phase 20 Limitation Note ---
      widget {
        note_definition {
          content          = "Phase 20 limitation: cdirective_bot traffic collapses into agent_id:openclaw at the host level (Telegram bot routes through the openclaw gateway and Phase 20 does not inject a per-bot custom header). Per-bot breakdown ships in Phase 21 (named OpenClaw skill registration). Do NOT cite agent_id:openclaw metrics as per-agent SLA until then."
          background_color = "yellow"
          font_size        = "14"
          text_align       = "left"
          show_tick        = false
          has_padding      = true
        }
      }
    }
  }
}

# --- DASHBOARD URL OUTPUT ---

output "agent_activity_dashboard_url" {
  description = "URL to the Agent Activity (CoSAI Visibility) dashboard in Datadog"
  value       = datadog_dashboard.agent_activity.url
}
