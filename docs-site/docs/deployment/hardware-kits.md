# Hardware Kits

Pre-configured hardware bundles for deploying HoneyAegis sensors. These kits are designed for quick deployment in offices, data centers, and remote locations.

## Kit A -- Raspberry Pi 4 Sensor ($89)

The entry-level kit for small offices and branch deployments.

| Component | Specification |
|---|---|
| Board | Raspberry Pi 4 Model B (2 GB RAM) |
| Storage | 32 GB microSD (Class A2, pre-flashed) |
| Power | Official USB-C power supply (5V/3A) |
| Case | Passive cooling aluminum case |
| Network | Cat6 Ethernet cable (1m) |

**Best for:** Single-sensor deployments, branch offices, home labs.

## Kit B -- Raspberry Pi 5 Sensor ($119)

Enhanced kit with more headroom for AI analysis and multi-protocol honeypots.

| Component | Specification |
|---|---|
| Board | Raspberry Pi 5 (4 GB RAM) |
| Storage | 64 GB microSD (Class A2, pre-flashed) |
| Power | USB-C PD power supply (5V/5A) |
| Case | Active cooling fan case |
| Network | Cat6 Ethernet cable (1m) |

**Best for:** Production sensors with local AI, multi-protocol capture.

## Kit C -- Enterprise Appliance ($249)

A compact x86 appliance for full-stack deployments with AI and monitoring.

| Component | Specification |
|---|---|
| Board | Intel N100 mini PC |
| RAM | 8 GB DDR4 |
| Storage | 256 GB NVMe SSD |
| Network | Dual Gigabit Ethernet |
| OS | Ubuntu Server 22.04 LTS (pre-installed) |

**Best for:** Central hubs, full-profile deployments, enterprise DMZ sensors.

## Assembly and Setup

### Kit A and Kit B (Raspberry Pi)

1. Insert the pre-flashed microSD card into the Pi.
2. Connect Ethernet and power.
3. Wait 2-3 minutes for first boot and Docker startup.
4. Access the dashboard at `http://<pi-ip>:3000`.
5. Log in with the credentials printed on the included card.

### Kit C (Enterprise Appliance)

1. Connect both Ethernet ports (one for management, one for honeypot traffic).
2. Connect power and wait for boot.
3. SSH into the appliance: `ssh admin@<appliance-ip>`.
4. Run the initial configuration wizard: `sudo honeyaegis-setup`.
5. Access the dashboard at `https://<appliance-ip>`.

## Network Placement

```
Internet ──► Firewall ──► DMZ Switch ──┬── HoneyAegis Sensor
                                        ├── Production Server
                                        └── Production Server
```

Place sensors on the same network segment as production servers to attract lateral movement traffic. Use firewall rules to forward common attack ports (22, 23, 445, 3306) to the sensor.

## Fleet Registration

After physical setup, register each sensor with your central hub:

```bash
# From the central HoneyAegis dashboard
# Navigate to Fleet > Add Sensor > Enter sensor details
# Copy the generated token to the sensor's .env file
```

See [Fleet Management](../features/fleet-management.md) for detailed fleet setup.

## MSP White-Label

MSP partners can order kits with custom branding:

- Custom boot splash and dashboard logo
- Pre-configured central hub URL
- Branded hardware labels and packaging
- Bulk pricing available for 10+ units

Contact the HoneyAegis team via [GitHub Discussions](https://github.com/thesecretchief/HoneyAegis/discussions) for white-label inquiries.

## Related Pages

- [Raspberry Pi Deployment](raspberry-pi.md) -- Software setup guide for RPi
- [Fleet Management](../features/fleet-management.md) -- Central sensor management
- [Deployment Matrix](../getting-started/deployment-matrix.md) -- All deployment options
