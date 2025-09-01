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
      const response = await fetch(`${this.localAgentURL}/health`);
      this.isLocalAgentConnected = response.ok;
      return this.isLocalAgentConnected;
    } catch (error) {
      this.isLocalAgentConnected = false;
      return false;
    }
  }

  async connectArduino(): Promise<any> {
    if (!this.isLocalAgentConnected) {
      throw new Error("Local agent not running. Please start CtrlHub Agent.");
    }
    
    const response = await fetch(`${this.localAgentURL}/hardware/connect`, {
      method: 'POST'
    });
    
    return await response.json();
  }

  async disconnectArduino(): Promise<any> {
    if (!this.isLocalAgentConnected) {
      throw new Error("Local agent not running. Please start CtrlHub Agent.");
    }
    
    const response = await fetch(`${this.localAgentURL}/hardware/disconnect`, {
      method: 'POST'
    });
    
    return await response.json();
  }

  async scanPorts(): Promise<any> {
    if (!this.isLocalAgentConnected) {
      throw new Error("Local agent not running. Please start CtrlHub Agent.");
    }
    
    const response = await fetch(`${this.localAgentURL}/hardware/ports`);
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

  async runDCMotorSimulation(parameters: any): Promise<any> {
    if (!this.isLocalAgentConnected) {
      return this.runJavaScriptSimulation(parameters);
    }
    
    const response = await fetch(`${this.localAgentURL}/simulation/dc_motor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parameters)
    });
    
    return await response.json();
  }

  connectWebSocket(): WebSocket | null {
    if (!this.isLocalAgentConnected) {
      return null;
    }
    
    const ws = new WebSocket('ws://localhost:8001/ws');
    
    ws.onopen = () => {
      console.log('CtrlHub Agent WebSocket connected');
    };
    
    ws.onerror = (error) => {
      console.error('CtrlHub Agent WebSocket error:', error);
    };
    
    return ws;
  }

  runJavaScriptSimulation(modelData: any): any {
    // Fallback simple simulation in JavaScript
    // For basic functionality when agent is not available
    console.log("Running fallback JavaScript simulation with data:", modelData);
    
    // Simple DC motor simulation fallback
    if (modelData.type === 'dc_motor') {
      const { voltage, resistance, inductance, ke, kt, j, b } = modelData.parameters || {};
      
      // Simple first-order approximation
      const timeConstant = inductance / resistance;
      const steadyStateCurrent = voltage / resistance;
      const steadyStateSpeed = (kt * steadyStateCurrent - b) / ke;
      
      // Generate simple response
      const time = Array.from({length: 100}, (_, i) => i * 0.01);
      const current = time.map(t => steadyStateCurrent * (1 - Math.exp(-t / timeConstant)));
      const speed = time.map(t => steadyStateSpeed * (1 - Math.exp(-t / (timeConstant * 2))));
      
      return {
        status: "success",
        data: { time, current, speed },
        message: "Fallback JavaScript simulation"
      };
    }
    
    return { 
      status: "success", 
      data: { message: "Basic JavaScript simulation completed" },
      message: "Fallback mode - install CtrlHub Agent for advanced simulations"
    };
  }
}

export default LocalAgentHandler;
