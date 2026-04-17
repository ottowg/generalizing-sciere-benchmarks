const dockerMode = import.meta.env.VITE_DOCKER_MODE === 'true'

export function useDockerMode() {
  return { dockerMode }
}
