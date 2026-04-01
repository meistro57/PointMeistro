<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        // Fix temp directory for Docker
        if (app()->environment('local', 'development')) {
            $tempDir = storage_path('framework/cache');
            
            if (!file_exists($tempDir)) {
                mkdir($tempDir, 0777, true);
            }
            
            putenv("TMPDIR={$tempDir}");
        }
    }
}
