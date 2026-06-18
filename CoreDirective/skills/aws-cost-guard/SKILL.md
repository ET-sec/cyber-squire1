---
name: aws-cost-guard
description: Monitor AWS costs, alert on running GPU instances, and suggest optimizations
---

# AWS Cost Guard

## When to Use
User asks about AWS costs, billing, instance status, or cost optimization.

## Critical Alert: GPU Instance

Instance `i-0bcb961f94bd8a51f` is a GPU instance that should STAY STOPPED. If running, it burns ~$0.50-3.00+/hr depending on type.

Check via `exec` tool on EC2:
```bash
aws ec2 describe-instances --instance-ids i-0bcb961f94bd8a51f --query 'Reservations[].Instances[].State.Name' --output text
```

If running, IMMEDIATELY alert:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "GPU INSTANCE RUNNING - i-0bcb961f94bd8a51f is ON. Estimated burn: $X/hr. Stop it NOW unless intentional."}
```

## Cost Estimates

| Resource | Monthly Est. |
|----------|-------------|
| t3.xlarge (on-demand) | ~$120 |
| EBS volumes (estimate 100GB gp3) | ~$8 |
| Cloudflare Tunnel | Free |
| Data transfer (estimate 50GB) | ~$4.50 |
| **Total baseline** | **~$133/mo** |

## Check Running Instances
```bash
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[].{ID:InstanceId,Type:InstanceType,Launch:LaunchTime}' --output table
```

## Check Idle Instances
```bash
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value=i-07bf58fe3de278a75 --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Average --output table
```
If average CPU < 5% for 24h, flag as potentially idle.

## EBS Volumes
```bash
aws ec2 describe-volumes --query 'Volumes[].{ID:VolumeId,Size:Size,Type:VolumeType,State:State}' --output table
```
Check for unattached volumes (State != in-use) -- these cost money for nothing.

## Cost Optimization Suggestions
1. **Reserved Instances:** t3.xlarge 1yr no-upfront saves ~35% ($78/mo vs $120/mo)
2. **Savings Plans:** Compute Savings Plan for flexible instance types
3. **Spot for GPU:** If GPU needed temporarily, use Spot (up to 90% savings)
4. **Right-sizing:** If CPU avg < 20%, consider t3.large (half cost)
5. **EBS cleanup:** Delete unattached volumes and old snapshots

## Weekly Cost Summary
Send via Telegram every Monday:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "AWS WEEKLY COST\nRunning instances: X\nGPU status: STOPPED (good)\nEstimated MTD: $X\nProjected monthly: $X\nAlerts: ..."}
```
