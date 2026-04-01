<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-950">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'PointMeistro') — PointMeistro</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="h-full text-gray-100 font-sans">

{{-- Sidebar --}}
<div class="flex h-full">
    <nav class="w-56 shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div class="px-5 py-5 border-b border-gray-800">
            <span class="text-xl font-bold tracking-tight text-white">Point<span class="text-blue-400">Meistro</span></span>
            <p class="text-xs text-gray-500 mt-0.5">Steel Fabrication · BLK360</p>
        </div>
        <ul class="flex-1 px-3 py-4 space-y-1 text-sm">
            <li>
                <a href="{{ route('dashboard') }}"
                   class="flex items-center gap-2.5 px-3 py-2 rounded-lg {{ request()->routeIs('dashboard') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white' }} transition">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6"/></svg>
                    Dashboard
                </a>
            </li>
            <li>
                <a href="{{ route('scans.index') }}"
                   class="flex items-center gap-2.5 px-3 py-2 rounded-lg {{ request()->routeIs('scans.*') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white' }} transition">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    Scans
                </a>
            </li>
            <li>
                <a href="/horizon" target="_blank"
                   class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    Horizon
                    <svg class="w-3 h-3 ml-auto opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
            </li>
        </ul>
        <div class="px-5 py-4 border-t border-gray-800 text-xs text-gray-600">
            v0.1-dev · Adams Steel
        </div>
    </nav>

    {{-- Main content --}}
    <div class="flex-1 flex flex-col overflow-hidden">
        <header class="h-14 bg-gray-900 border-b border-gray-800 flex items-center px-6 shrink-0">
            <h1 class="text-sm font-semibold text-gray-200">@yield('title', 'Dashboard')</h1>
        </header>
        <main class="flex-1 overflow-y-auto p-6">
            @yield('content')
        </main>
    </div>
</div>

</body>
</html>
