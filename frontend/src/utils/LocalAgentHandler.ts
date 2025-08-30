/*
CtrlHub Local Agent Handler for Frontend Communication
Replaces Web Serial API calls with HTTP communication to desktop agent
*/

import { useState, useEffect, useCallback } from 'react';

interface LocalAgentConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

interface ArduinoDevice {
  port: string;
  description: string;
  manufacturer?: string;
  connected: boolean;
}

interface MotorData {
  speed: number;
  current: number;
  voltage: number;
  encoder_position: number;
  timestamp: number;
}

interface SimulationConfig {
  mode: 'offline' | 'hardware' | 'hybrid';
  duration: number;
  dt: number;
  sample_rate: number;
  real_time: boolean;
}

interface SimulationResults {
  time_data: number[];
  input_data: number[];
  output_data: number[];
  current_data: number[];
  analysis?: {
    steady_state_value: number;
    rise_time?: number;
    settling_time?: number;
    overshoot_percent: number;
    peak_time: number;
  };
}

interface PIDParameters {
  Kp: number;
  Ki: number;
  Kd: number;
  output_min: number;
  output_max: number;
}

interface MotorParameters {
  R: number;  // Resistance (Ohms)
  L: number;  // Inductance (H)
  J: number;  // Inertia (kg⋅m²)
  b: number;  // Friction coefficient (N⋅m⋅s/rad)
  Kt: number; // Torque constant (N⋅m/A)
  Ke: number; // Back-EMF constant (V⋅s/rad)
}

class LocalAgentError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'LocalAgentError';
  }
}

export class LocalAgentHandler {
  private config: LocalAgentConfig;
  private ws: WebSocket | null = null;
  private eventListeners: Map<string, Set<Function>> = new Map();
  private connectionState: 'disconnected' | 'connecting' | 'connected' = 'disconnected';
  private heartbeatInterval: number | null = null;

  constructor(config: Partial<LocalAgentConfig> = {}) {
    this.config = {
      baseUrl: 'http://localhost:8001',
      timeout: 5000,
      retryAttempts: 3,
      retryDelay: 1000,
      ...config
    };
  }

  // Connection Management
  async checkConnection(): Promise<boolean> {
    try {
      const response = await this.makeRequest('/health', 'GET');
      return response.status === 'healthy';
    } catch (error) {
      console.warn('Local agent not available:', error);
      return false;
    }
  }

  async connect(): Promise<void> {
    if (this.connectionState === 'connected') {
      return;
    }

    this.connectionState = 'connecting';
    
    // Check HTTP connection first
    const isHealthy = await this.checkConnection();
    if (!isHealthy) {
      this.connectionState = 'disconnected';
      throw new LocalAgentError('Desktop agent is not running or not accessible');
    }

    // Establish WebSocket for real-time data
    try {
      await this.connectWebSocket();
      this.connectionState = 'connected';
      this.startHeartbeat();
      this.emit('connected');
    } catch (error) {
      this.connectionState = 'disconnected';
      throw error;
    }
  }

  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = this.config.baseUrl.replace('http', 'ws') + '/ws';
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected to local agent');
        resolve();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected from local agent');
        this.connectionState = 'disconnected';
        this.stopHeartbeat();
        this.emit('disconnected');
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(new LocalAgentError('WebSocket connection failed'));
      };
      
      // Timeout for connection
      setTimeout(() => {
        if (this.ws?.readyState !== WebSocket.OPEN) {
          this.ws?.close();
          reject(new LocalAgentError('WebSocket connection timeout'));
        }
      }, this.config.timeout);
    });
  }

  private handleWebSocketMessage(data: any): void {
    switch (data.type) {
      case 'motor_data':
        this.emit('motorData', data.payload);
        break;
      case 'simulation_data':
        this.emit('simulationData', data.payload);
        break;
      case 'arduino_connected':
        this.emit('arduinoConnected', data.payload);
        break;
      case 'arduino_disconnected':
        this.emit('arduinoDisconnected', data.payload);
        break;
      case 'error':
        this.emit('error', new LocalAgentError(data.message, data.code));
        break;
      default:
        console.warn('Unknown WebSocket message type:', data.type);
    }
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(async () => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      } else {
        // Try to reconnect
        try {
          await this.connectWebSocket();
        } catch (error) {
          console.error('Heartbeat reconnection failed:', error);
        }
      }
    }, 30000); // 30 second heartbeat
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connectionState = 'disconnected';
  }

  // Arduino Hardware Interface
  async scanArduinoDevices(): Promise<ArduinoDevice[]> {
    const response = await this.makeRequest('/arduino/scan', 'GET');
    return response.devices;
  }

  async connectArduino(port: string): Promise<void> {
    await this.makeRequest('/arduino/connect', 'POST', { port });
  }

  async disconnectArduino(): Promise<void> {
    await this.makeRequest('/arduino/disconnect', 'POST');
  }

  async getArduinoStatus(): Promise<{ connected: boolean; port?: string }> {
    return await this.makeRequest('/arduino/status', 'GET');
  }

  // Motor Control
  async setMotorVoltage(voltage: number): Promise<void> {
    await this.makeRequest('/motor/voltage', 'POST', { voltage });
  }

  async getMotorData(): Promise<MotorData> {
    return await this.makeRequest('/motor/data', 'GET');
  }

  async setMotorParameters(params: MotorParameters): Promise<void> {
    await this.makeRequest('/motor/parameters', 'POST', params);
  }

  async getMotorParameters(): Promise<MotorParameters> {
    return await this.makeRequest('/motor/parameters', 'GET');
  }

  // PID Controller
  async setPIDParameters(params: PIDParameters): Promise<void> {
    await this.makeRequest('/pid/parameters', 'POST', params);
  }

  async getPIDParameters(): Promise<PIDParameters> {
    return await this.makeRequest('/pid/parameters', 'GET');
  }

  async setPIDSetpoint(setpoint: number): Promise<void> {
    await this.makeRequest('/pid/setpoint', 'POST', { setpoint });
  }

  async enablePID(enable: boolean): Promise<void> {
    await this.makeRequest('/pid/enable', 'POST', { enable });
  }

  async getPIDStatus(): Promise<{ enabled: boolean; setpoint: number; output: number }> {
    return await this.makeRequest('/pid/status', 'GET');
  }

  // Simulation Engine
  async runStepResponse(config: SimulationConfig, stepVoltage: number): Promise<SimulationResults> {
    return await this.makeRequest('/simulation/step_response', 'POST', {
      config,
      step_voltage: stepVoltage
    });
  }

  async runParameterIdentification(config: SimulationConfig): Promise<any> {
    return await this.makeRequest('/simulation/parameter_identification', 'POST', { config });
  }

  async startRealTimeSimulation(config: SimulationConfig): Promise<void> {
    await this.makeRequest('/simulation/start_realtime', 'POST', { config });
  }

  async stopRealTimeSimulation(): Promise<void> {
    await this.makeRequest('/simulation/stop_realtime', 'POST');
  }

  async getSimulationStatus(): Promise<{ running: boolean; mode?: string }> {
    return await this.makeRequest('/simulation/status', 'GET');
  }

  // Data Export
  async exportData(format: 'json' | 'csv'): Promise<Blob> {
    const response = await fetch(`${this.config.baseUrl}/data/export?format=${format}`, {
      method: 'GET',
      headers: { 'Accept': format === 'json' ? 'application/json' : 'text/csv' }
    });
    
    if (!response.ok) {
      throw new LocalAgentError(`Export failed: ${response.statusText}`, 'EXPORT_ERROR', response.status);
    }
    
    return await response.blob();
  }

  // Event System
  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(callback);
  }

  off(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  private emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Event callback error for ${event}:`, error);
        }
      });
    }
  }

  // HTTP Request Helper
  private async makeRequest(
    endpoint: string, 
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET', 
    data?: any
  ): Promise<any> {
    const url = `${this.config.baseUrl}${endpoint}`;
    
    for (let attempt = 0; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: data ? JSON.stringify(data) : undefined,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ message: response.statusText }));
          throw new LocalAgentError(
            errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            errorData.code || 'HTTP_ERROR',
            response.status
          );
        }
        
        return await response.json();
        
      } catch (error) {
        if (attempt === this.config.retryAttempts) {
          if (error instanceof LocalAgentError) {
            throw error;
          }
          throw new LocalAgentError(
            `Request failed after ${this.config.retryAttempts + 1} attempts: ${error.message}`,
            'REQUEST_FAILED'
          );
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * (attempt + 1)));
      }
    }
  }

  // Utility Methods
  getConnectionState(): 'disconnected' | 'connecting' | 'connected' {
    return this.connectionState;
  }

  isConnected(): boolean {
    return this.connectionState === 'connected';
  }

  getConfig(): LocalAgentConfig {
    return { ...this.config };
  }

  updateConfig(newConfig: Partial<LocalAgentConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }
}

// React Hook for LocalAgent
export function useLocalAgent() {
  const [agent] = useState(() => new LocalAgentHandler());
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleConnected = () => {
      setConnected(true);
      setConnecting(false);
      setError(null);
    };

    const handleDisconnected = () => {
      setConnected(false);
      setConnecting(false);
    };

    const handleError = (err: LocalAgentError) => {
      setError(err.message);
      setConnecting(false);
    };

    agent.on('connected', handleConnected);
    agent.on('disconnected', handleDisconnected);
    agent.on('error', handleError);

    return () => {
      agent.off('connected', handleConnected);
      agent.off('disconnected', handleDisconnected);
      agent.off('error', handleError);
      agent.disconnect();
    };
  }, [agent]);

  const connect = useCallback(async () => {
    if (connected || connecting) return;
    
    setConnecting(true);
    setError(null);
    
    try {
      await agent.connect();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
      setConnecting(false);
    }
  }, [agent, connected, connecting]);

  const disconnect = useCallback(() => {
    agent.disconnect();
  }, [agent]);

  return {
    agent,
    connected,
    connecting,
    error,
    connect,
    disconnect
  };
}

export default LocalAgentHandler;