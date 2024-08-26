# inSync Backend

The backend for the inSync game, where players try to align their thinking on scales of opposing concepts. This project is currently in the development stage.

## Overview

inSync is a game designed to test how closely players' thoughts align. Each game, players are presented with three scales of opposing concepts, such as **Hot** and **Cold** or **Big** and **Small**. A marker is placed somewhere on each scale, and the player provides a clue to the team to indicate the marker's position. The other players then attempt to place their group marker as close as possible to the original position based on the clue.

## Technology Stack

- **Python**
- **MySQL**
- **Docker**
- **WebSockets**
- **Auth tokens**

## Prerequisites

- Ensure Docker and Docker Compose are installed on your machine.

## Installation and Setup

1. **Clone the Repository**
2. **On first run:** docker-compose up --build
3. **On subsequent runs:** docker-compose up
4. **Seed the data base:** from within the python container (insync_web) run: flask seed:all

## Usage
The backend serves a separate repository that provides the frontend. The game logic is centered around WebSockets and Auth tokens to ensure fast and secure communication between the backend and frontend.

