# Contributing to FocusDNA AI

Thank you for your interest in contributing to FocusDNA AI! We welcome contributions from developers of all skill levels.

---

## Code of Conduct

By participating in this project, you agree to abide by our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please report unacceptable behavior to `community@focusdna.ai`.

---

## Development Workflow

1. **Fork & Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/FocusDNA-AI.git
   cd FocusDNA-AI
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install Dependencies**:
   ```bash
   # Web Frontend
   npm --prefix apps/web install

   # Python Backend & ML
   pip install -r apps/api/requirements.txt
   ```

4. **Run Local Development Servers**:
   - Backend: `PYTHONPATH=apps/api:ml python3 -m uvicorn main:app --host 127.0.0.1 --port 8000`
   - Frontend: `npm --prefix apps/web run dev`

5. **Run Tests & Verify Build**:
   ```bash
   # Pytest Backend Suite
   PYTHONPATH=apps/api:ml python3 -m pytest apps/api/tests

   # Next.js Production Build Verification
   npm --prefix apps/web run build
   ```

6. **Submit a Pull Request (PR)**:
   - Push your branch: `git push origin feature/your-feature-name`
   - Open a Pull Request against the `main` branch with clear description notes.
