#!/bin/bash
sleep 15m
curl -X POST https://api.github.com/repos/Acheirial/openit/dispatches -H "Accept: application/vnd.github+json" -H "Authorization: token $1" --data '{"event_type": "Webhook"}' --silent
