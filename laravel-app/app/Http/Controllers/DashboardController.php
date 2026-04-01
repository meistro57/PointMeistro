<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Facades\Http;

class DashboardController extends Controller
{
    public function index()
    {
        $stats = [
            'queued_jobs'  => DB::table('jobs')->count(),
            'failed_jobs'  => DB::table('failed_jobs')->count(),
            'users'        => DB::table('users')->count(),
        ];

        $segmenterUp = $this->checkSegmenter();
        $redisUp      = $this->checkRedis();

        return view('dashboard', compact('stats', 'segmenterUp', 'redisUp'));
    }

    private function checkSegmenter(): bool
    {
        try {
            $response = Http::timeout(2)->get('http://segmenter:8001/health');
            return $response->successful();
        } catch (\Throwable) {
            return false;
        }
    }

    private function checkRedis(): bool
    {
        try {
            return Redis::ping() === true || Redis::ping() === 'PONG';
        } catch (\Throwable) {
            return false;
        }
    }
}
