import { login, signup } from './actions'

export default function LoginPage() {
  return (
    <main className="h-screen flex items-center justify-center bg-blue-700 p-6">
      <div className="flex flex-col items-center">
        <h1 className="text-orange-500 text-6xl font-bold mb-6">NUS Supper Hitch</h1>
        <div className="bg-gray-900 p-8 rounded-lg shadow-md w-96">
          <form>
            <label htmlFor="email">Email:</label>
            <input id="email" name="email" type="email" required 
            className="mb-4 w-full p-3 rounded-md border border-gray-700 bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"/>
            <label htmlFor="password">Password:</label>
            <input id="password" name="password" type="password" required 
            className="mb-4 w-full p-3 rounded-md border border-gray-700 bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"/>
            <button formAction={login}
            className="w-full mb-2 p-3 rounded-md bg-blue-600 text-white hover:bg-blue-700 focus:outline-none">Log in</button>
            <button formAction={signup} className="w-full mb-2 p-3 rounded-md bg-blue-600 text-white hover:bg-blue-700 focus:outline-none">Sign up</button>
          </form>
        </div>
      </div>
    </main>
  )
}