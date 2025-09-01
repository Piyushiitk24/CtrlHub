class LocalAgentHandler {
  private localAgentURL: string;
  private cloudBackendURL: string | null;
  public isLocalAgentConnected: boolean;

  constructor() {
    this.localAgentURL = 'http://localhost:8001';
    this.cloudBackendURL = process.env.REACT_APP_CLOUD_URL || null;
    this.isLocalAgentConnected = false;
  }

  async checkLocalAgent(): Promise<boolean> {
    try {
      const response = await fetch(`${this.localAgentURL}/`);
      this.isLocalAgentConnected = response.ok;
      return this.isLocalAgentConnected;
    } catch (error) {
      this.isLocalAgentConnected = false;
      return false;
    }
  }

  async connectArduino(): Promise<any> {
    if (!this.isLocalAgentConnected) {
      throw new Error("Local agent not running. Please start VirtualLab Agent.");
    }
    
    const response = await fetch(`${this.localAgentURL}/hardware/connect`, {
      method: 'POST'
    });
    
    return await response.json();
  }

  async runSimulation(modelData: any): Promise<any> {
    if (!this.isLocalAgentConnected) {
      // Fallback to simple JavaScript simulation
      return this.runJavaScriptSimulation(modelData);
    }
    
    // Use powerful Python simulation
    const response = await fetch(`${this.localAgentURL}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(modelData)
    });
    
    return await response.json();
  }

  runJavaScriptSimulation(modelData: any): any {
    // Fallback simple simulation in JavaScript
    // For basic functionality when agent is not available
    console.log("Running fallback JavaScript simulation with data:", modelData);
    return { status: "ran js simulation" };
  }
}

export default LocalAgentHandler;
